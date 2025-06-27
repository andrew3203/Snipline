import json
from typing import NamedTuple

from src.utils.serialise import to_json_list


def get_urls() -> list[dict[str, str]]:
    with open("urls.json", "r", encoding="utf-8") as f:
        return json.loads(f.read())


def update_urls(data: list[dict[str, str]]) -> list[dict[str, str]]:
    with open("urls.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2))
    

def save(data: list[NamedTuple], i: int):
    with open(f"result-{i}.json", "w", encoding="utf-8") as f:
        f.write(to_json_list(data))