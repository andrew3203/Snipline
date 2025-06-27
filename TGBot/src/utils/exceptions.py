class CoreException(Exception):
    """
    Базовы класс ошибки
    """

    def __init__(
        self,
        msg: str,
        code: int,
        data: dict | None = None,
        *args: object,
    ) -> None:
        self.msg = msg
        self.code = code
        self.data = data
        super().__init__(*args)
 