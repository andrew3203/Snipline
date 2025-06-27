import json
from typing import NamedTuple
from datetime import datetime

KEYS = set([
    "source_url",
    "url",
    "title",
    "top_img",
    "top_image",
    "meta_img",
    "images",
    "meta_keywords",
    "keywords",
    "text",
    "meta_description",
    "meta_data",
    "additional_data",
    "publish_date",
])

def default_serializer(x):
    if isinstance(x, datetime):
        return x.isoformat()
    if isinstance(x, tuple) and hasattr(x, "_fields"):
        d = x._asdict()
        d.pop("html", None)
        return d
    if hasattr(x, "__dict__"):
        return {k: default_serializer(v) for k, v in x.__dict__.items() if k in KEYS}
    if isinstance(x, dict):
        return x
    return str(x)  # fallback

def to_json(obj: NamedTuple) -> str:
    return json.dumps(
        obj._asdict(),
        default=default_serializer,
        ensure_ascii=False,
        indent=2,
    )

def to_json_list(items: list[NamedTuple]) -> str:
    data = []
    for item in items:
        d = item._asdict()
        d.pop("html", None)
        data.append(d)
    return json.dumps(
        data,
        default=default_serializer,
        ensure_ascii=False,
        indent=2,
    )