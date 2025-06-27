from pydantic import BaseModel, Field
from typing import Literal


class Button(BaseModel):
    callback: str = Field(description="callback of btn")
    url: str | None = Field(None, description="Url")
    pay: bool | None = Field(description="Pay", default=None)

class ButtonObj(BaseModel):
    type: Literal["static", "dynamic"] = Field(description="Type of btn", default="static")
    buttons: list[list[Button]] | None = Field(None, description="Кнопки для выбора действия")
    buttons_gen_func: str | None = Field(description="Name of generation function", default=None)

class MessageNode(BaseModel):
    type: Literal["message"] = Field(description="Тип узла — сообщение")
    btn: ButtonObj | None = Field(None, description="Кнопки для выбора действия")
    edit: bool = Field(False, description="Edit prev message")
    next: str | None = Field(None, description="Следующий узел после сообщения (если нет input или кнопок)")


class Condition(BaseModel):
    if_: str | None = Field(None, alias="if", description="Условие, которое проверяется (если выполняется — переход к 'goto')")
    else_: str | None = Field(None, alias="else", description="Переход, если ни одно условие не выполнено")
    goto: str | None = Field(None, description="Целевой узел перехода при выполнении условия")


class ConditionNode(BaseModel):
    type: Literal["condition"] = Field(description="Тип узла — условие")
    conditions: list[Condition] = Field(description="Список условий для проверки")


class FunctionNode(BaseModel):
    type: Literal["function"] = Field(description="Тип узла — вызов функции")
    name: str = Field(description="Имя функции, которую необходимо вызвать")
    next: str = Field(description="Следующий узел после выполнения функции")


class SubflowNode(BaseModel):
    type: Literal["subflow"] = Field(description="Тип узла — запуск подфлоу")
    flow: str = Field(description="Имя подфлоу (подпроцесса)")
    entry: str = Field(description="Точка входа в подфлоу")


class EndNode(BaseModel):
    type: Literal["end"] = Field(description="Тип узла — завершение сценария")

class InputNode(BaseModel):
    type: Literal["input"] = Field(description="Тип узла — ввод текста пользователем")
    save_to: str = Field(description="Куда сохранить ответ пользователя")
    next: str = Field(description="Куда перейти после ввода")

Node = MessageNode | ConditionNode | FunctionNode | SubflowNode | EndNode | InputNode


class FlowDefinition(BaseModel):
    start_node: str = Field(description="Имя стартового узла")
    nodes: dict[str, Node] = Field(description="Словарь всех узлов сценария, по имени узла")
