from src.application.llm.llm_base import LLMBase
from src.models.news import NewsItem
from src.repository.llm import ChatCompletionRequest, Message


class LLMReport(LLMBase):
    def __init__(self):
        super().__init__("src/prompts/report")
        self.i18n = {
            "ru": {
                "p": "Дата публикации",
                "u": "Ссылка на статью",
                "c": "Категория статьи",
                "s": "Под категории",
                "l": "Локации",
                "n": "Имена в статье",
                "a": "Краткое содержание статьи",
                "analyze": (
                    "Ты должен проанализировать данные новости и сделать выводы, "
                    "а так-же предположить очень кратко какие будут последтсвия если это уместно."
                ),
                "analyze2": (
                    "Ты должен проанализировать данные новости и сделать выводы, "
                    "а так-же предположить очень кратко какие будут последтсвия если это уместно. "
                    "Ниже вопрос пользовател, ответь на него\n\n"
                ),
                "q": "Пользователь написал вопрос, скажи что он имел в виду",
                "error": "Мало новостей",
            },
            "en": {
                "p": "Published at",
                "u": "URL",
                "c": "Category",
                "s": "Subcategories",
                "l": "Locations",
                "n": "Names",
                "a": "Article text",
                "analyze": (
                    "You must analyze the news data and draw conclusions, "
                    "as well as very briefly suggest what the consequences will be if appropriate. "
                    "Ниже вопрос пользовател, ответь на него\n\n"
                ),
                "analyze2": (
                    "You must analyze the news data and draw conclusions, "
                    "as well as very briefly suggest what the consequences will be if appropriate.\n\n"
                ),
                "q": "Пользователь написал вопрос, скажи что он имел в виду",
                "error": "Мало новостей",
            },
        }

    async def get_report(self, data: list[NewsItem], answer_lang: str, **kwagrs) -> str:
        lang = answer_lang if answer_lang in self.i18n.keys() else "en"
        if not self.promts:
            await self.load_promts()
        self.promts[lang] = self.promts[lang] + self.i18n[lang]["analyze"]

        if len(data) == 0:
            return self.i18n[lang]["error"]

        text = "\n\n".join(
            [
                (
                    f"{self.i18n[lang]['p']}: {i.published_at.strftime('%d/%m/%Y, %H:%M')}, "
                    f"{self.i18n[lang]['u']}: {i.source_url}\n"
                    # f"{self.i18n[lang]['c']}: {i.category}, "
                    # f"{self.i18n[lang]['s']}: {', '.join(i.subcategories)}, "
                    f"{self.i18n[lang]['l']}: {', '.join(i.locations)}\n"
                    f"{self.i18n[lang]['n']}: {', '.join(i.names)}, "
                    f"{self.i18n[lang]['a']}:\n{i.summary}"
                )
                for i in data
            ]
        )
        resp, _ = await self.get(text=text, lang=lang, **kwagrs)
        return resp

    async def get_report_with_payload(
        self, data: list[NewsItem], answer_lang: str, question: str, **kwagrs
    ) -> str:
        lang = answer_lang if answer_lang in self.i18n.keys() else "en"
        if not self.promts:
            await self.load_promts()
        payload = ChatCompletionRequest(
            messages=[
                Message(role="system", content=self.i18n[lang]["q"]),
                Message(role="user", content=question),
            ],
            temperature=0.3,
            top_p=0.9,
            max_tokens=3000,
            max_completion_tokens=1000,
        )
        response = await self.agent.chat_completion(payload=payload)
        lang = answer_lang if answer_lang in self.i18n.keys() else "en"
        self.promts[lang] = (
            self.promts[lang]
            + self.i18n[lang]["analyze"]
            + response["choices"][0]["message"]["content"]
        )
        text = "\n\n".join(
            [
                (
                    f"{self.i18n[lang]['p']}: {i.published_at.strftime('%d/%m/%Y, %H:%M')}, "
                    f"{self.i18n[lang]['u']}: {i.source_url}\n"
                    # f"{self.i18n[lang]['c']}: {i.category}, "
                    # f"{self.i18n[lang]['s']}: {', '.join(i.subcategories)}, "
                    f"{self.i18n[lang]['l']}: {', '.join(i.locations)}\n"
                    f"{self.i18n[lang]['n']}: {', '.join(i.names)}, "
                    f"{self.i18n[lang]['a']}:\n{i.summary}"
                )
                for i in data
            ]
        )
        resp, _ = await self.get(text=text, lang=lang, max_completion_tokens=1000)
        return resp
