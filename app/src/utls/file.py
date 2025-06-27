import asyncio
import os
from typing import Any, Literal
import orjson


def _read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


async def read_file(path: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _read_file, path)


async def read_json_file(path: str) -> dict[str, Any]:
    data = await read_file(path=path)
    return orjson.loads(data)


async def read_all_from_dir(
    directory: str, file_format: Literal["json", "txt"]
) -> dict[str, Any]:
    loop = asyncio.get_event_loop()
    files = await loop.run_in_executor(None, lambda: os.listdir(directory))

    func = read_file if file_format == "txt" else read_json_file
    file_format = f".{file_format}"
    json_files = [f for f in files if f.endswith(file_format)]

    tasks = [func(os.path.join(directory, filename)) for filename in json_files]

    contents = await asyncio.gather(*tasks)

    return {
        filename.replace(file_format, ""): content
        for filename, content in zip(json_files, contents)
    }
