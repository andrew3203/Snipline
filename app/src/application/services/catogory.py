from rapidfuzz import process, fuzz
from sqlmodel import select
from src.models.category import NewsCategory
from src.models.dictionary import Dictionary
from sqlmodel.ext.asyncio.session import AsyncSession


class NewsCategoryService:
    def __init__(self):
        self.categories_by_id: dict[int, NewsCategory] = {}
        self.categories_by_key: dict[str, NewsCategory] = {}
        self.translations: dict[str, dict[str, str]] = {}
        self.translation_lookup: dict[tuple[str, str], str] = {}
        self.data: dict[str, dict[str, list[dict[str, str | int]] | int]] = {}

    async def on_load(self, session: AsyncSession) -> None:
        categories_result = await session.exec(select(NewsCategory))
        dictionaries_result = await session.exec(select(Dictionary))

        categories = categories_result.all()
        dictionaries = dictionaries_result.all()

        self.categories_by_id = {c.id: c for c in categories}
        self.categories_by_key = {c.key: c for c in categories}
        self.translations = {d.key: d.data for d in dictionaries}

        self.translation_lookup = {}
        for key, lang_map in self.translations.items():
            for lang, value in lang_map.items():
                if value:
                    self.translation_lookup[(lang, value.strip().lower())] = key

        for c in categories:
            if c.key not in self.data:
                if c.parent_id is None:
                    self.data[c.key] = {
                        "id": c.id,
                        "name": self.translations[c.key],
                        "subcategories": [],
                    }
                else:
                    # надо подагегорию завестив
                    pass

    def get_categories_list(self, lang: str):
        list[str]

    def get_category_name_by_id(self, category_id: int, lang: str) -> str | None:
        category = self.categories_by_id.get(category_id)
        if not category:
            return None
        return self.translations.get(category.key, {}).get(lang)

    def get_subcategory_names(
        self, subcategories: list[int | str], lang: str
    ) -> list[str]:
        names = []
        for item in subcategories:
            if isinstance(item, int):
                category = self.categories_by_id.get(item)
                if category:
                    name = self.translations.get(category.key, {}).get(lang)
                    if name:
                        names.append(name)
            elif isinstance(item, str):
                names.append(item)
        return names

    def match_category_by_text(self, text: str, lang: str) -> list[int]:
        """
        Возвращает до 3-х category_id по частичному совпадению одного текста.
        Учитывает родительскую категорию.
        """
        if not text:
            return []

        norm = text.strip().lower()

        lang_keys = {
            key: self.translations.get(key, {}).get(lang, "").strip().lower()
            for key in self.categories_by_key
        }
        lang_keys = {k: v for k, v in lang_keys.items() if v}

        matched_keys = set()
        matches = process.extract(
            norm, lang_keys, scorer=fuzz.partial_ratio, limit=5, score_cutoff=60
        )
        # matches: list of (key, score, index)

        for key, _, _ in matches:
            matched_keys.add(key)

        category_ids = []
        seen_parents = set()

        for key in matched_keys:
            cat = self.categories_by_key.get(key)
            if not cat:
                continue
            parent_id = cat.parent_id or cat.id
            if parent_id not in seen_parents:
                seen_parents.add(parent_id)
                category_ids.append(parent_id)
            if len(category_ids) >= 3:
                break

        return category_ids

    def match_subcategories_by_texts(
        self, category_id: int | None, inputs: list[str], lang: str
    ) -> list[int | str]:
        """
        Возвращает подкатегории по максимальному совпадению: id или оригинальный текст.
        """
        result: list[int | str] = []
        inputs = [s.strip().lower() for s in inputs if s]
        if not inputs:
            return result

        subcats = [
            cat
            for cat in self.categories_by_id.values()
            if cat.parent_id == category_id or category_id is None
        ]

        lang_keys = {
            self.translations.get(sub.key, {}).get(lang, "").strip().lower(): sub.key
            for sub in subcats
            if self.translations.get(sub.key, {}).get(lang)
        }

        for raw in inputs:
            if not raw:
                continue
            match = process.extractOne(
                raw, lang_keys, scorer=fuzz.partial_ratio, score_cutoff=60
            )
            if match:
                sub_key = lang_keys[match[0]]
                result.append(self.categories_by_key[sub_key].id)
            else:
                result.append(raw)

        return result

    def resolve_category(self, text: str, lang: str) -> int | None:
        """
        Определяет category_id по тексту:
        - сначала пытается найти точное совпадение,
        - если не найдено — ищет по частичному совпадению.
        """
        if not text:
            return None

        norm = text.strip().lower()

        # Шаг 1 — точное соответствие
        key = self.translation_lookup.get((lang, norm))
        if key and key in self.categories_by_key:
            cat = self.categories_by_key[key]
            return cat.parent_id or cat.id

        # Шаг 2 — частичное совпадение
        matched_ids = self.match_category_by_text(text, lang)
        return matched_ids[0] if matched_ids else None

    def resolve_subcategories(
        self, category_id: int | None, texts: list[str], lang: str
    ) -> list[int | str]:
        """
        Сначала ищет подкатегории по точному переводу, потом по частичному совпадению.
        """
        exact_matches = []
        unresolved = []

        for raw in texts:
            if not raw:
                continue
            norm = raw.strip().lower()
            key = self.translation_lookup.get((lang, norm))
            if key:
                cat = self.categories_by_key.get(key)
                if cat and (cat.parent_id == category_id or category_id is None):
                    exact_matches.append(cat.id)
                    continue
            unresolved.append(raw)

        # fuzzy-поиск по тем, что не удалось "честно"
        fuzzy_matches = self.match_subcategories_by_texts(category_id, unresolved, lang)

        return exact_matches + fuzzy_matches
