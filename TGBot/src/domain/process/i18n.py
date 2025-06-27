from src.utils.singelon import SingletonMeta
import orjson


class Localization(metaclass=SingletonMeta):
    def __init__(self):
        path = "src/utils/i18n.json"
        with open(path, "r", encoding="utf-8") as f:
            self.data: dict[str, dict[str, str]] = orjson.loads(f.read())
    
    def get(self, lang: str, key: str) -> str:
        try:
            return self.data[lang][key]
        except KeyError:
            return self.data["en"][key]
