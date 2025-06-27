from datetime import datetime, timezone, timedelta
import re

TZ_OFFSETS = {
    "UTC": 0,
    "GMT": 0,
    "EDT": -4 * 60,
    "EST": -5 * 60,
    "PDT": -7 * 60,
    "PST": -8 * 60,
    "CET": 1 * 60,
    "CEST": 2 * 60,
}

def parse_datetime_with_timezone(dt_str: str) -> datetime:
    # 1. Формат: "Wed, 16 Apr 2025 15:47:32 +0300"
    match = re.match(r"(\w{3}, \d{2} \w{3} \d{4} \d{2}:\d{2}:\d{2}) ([+-])(\d{2})(\d{2})", dt_str)
    if match:
        date_part, sign, hours, minutes = match.groups()
        offset = int(hours) * 60 + int(minutes)
        if sign == '-':
            offset = -offset
        tz = timezone(timedelta(minutes=offset))
        dt = datetime.strptime(date_part, "%a, %d %b %Y %H:%M:%S")
        return dt.replace(tzinfo=tz)

    # 2. Формат: "2025-04-17 20:37:25" (без зоны, считаем как UTC)
    match = re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", dt_str)
    if match:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        return dt.replace(tzinfo=timezone.utc)

    # 3. Формат: "Thu, 17 Apr 2025 17:52:03 GMT"
    match = re.match(r"(\w{3}, \d{2} \w{3} \d{4} \d{2}:\d{2}:\d{2}) GMT", dt_str)
    if match:
        date_part = match.group(1)
        dt = datetime.strptime(date_part, "%a, %d %b %Y %H:%M:%S")
        return dt.replace(tzinfo=timezone.utc)

    # 4. Формат: "2025-04-17T20:21:47Z" (ISO 8601, UTC)
    match = re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", dt_str)
    if match:
        dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.replace(tzinfo=timezone.utc)

    # 5. Формат: "2025-04-17T16:29:45-04:00" (ISO 8601 с числовой зоной)
    match = re.match(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})([+-])(\d{2}):(\d{2})", dt_str)
    if match:
        date_part, sign, hours, minutes = match.groups()
        offset = int(hours) * 60 + int(minutes)
        if sign == '-':
            offset = -offset
        tz = timezone(timedelta(minutes=offset))
        dt = datetime.strptime(date_part, "%Y-%m-%dT%H:%M:%S")
        return dt.replace(tzinfo=tz)

    # 6. Формат: "Wed, 16 Apr 2025 20:40:34 EDT" (аббревиатура временной зоны)
    match = re.match(r"(\w{3}, \d{2} \w{3} \d{4} \d{2}:\d{2}:\d{2}) (\w{2,4})", dt_str)
    if match:
        date_part, tz_abbr = match.groups()
        offset_minutes = TZ_OFFSETS.get(tz_abbr.upper())
        if offset_minutes is not None:
            tz = timezone(timedelta(minutes=offset_minutes))
            dt = datetime.strptime(date_part, "%a, %d %b %Y %H:%M:%S")
            return dt.replace(tzinfo=tz)

    raise ValueError(f"Неизвестный формат даты: {dt_str}")


def clean_news(raw_text: str) -> str:
    raw_text = re.sub(r'https?://\S+', '', raw_text).strip("\n")
    raw_text = re.sub(r'http?://\S+', '', raw_text).strip("\n")
    # 1. Удаление дубликатов строк (оставим уникальные)
    lines = raw_text.splitlines()
    unique_lines = []
    seen = set()
    for line in lines:
        line = line.strip()
        if line and line not in seen:
            unique_lines.append(line)
            seen.add(line)

    # 2. Удаление ISO-дат (в формате 2025-04-19T16:22:00+03:00)
    clean_lines = [re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}', '', line) for line in unique_lines]

    # 3. Удаление email, телефонов и чисел без контекста
    clean_lines = [re.sub(r'\S+@\S+|\d[\d\s-]{5,}|\d{3,}', '', line) for line in clean_lines]

    # 5. Удаление повторений в заголовках
    final_lines = []
    for line in clean_lines:
        if not final_lines or final_lines[-1] != line:
            final_lines.append(line)

    # 6. Объединение обратно в текст
    result = '\n'.join(final_lines)
    
    # 7. Удаление лишних пробелов
    result = re.sub(r'\n\s*\n', '\n\n', result).strip()
    return result