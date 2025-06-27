from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from tqdm import tqdm

# --- Summary model (русский mBART) ---
sum_model_name = "IlyaGusev/mbart_ru_sum_gazeta"
sum_tokenizer = AutoTokenizer.from_pretrained(sum_model_name)
sum_model = AutoModelForSeq2SeqLM.from_pretrained(sum_model_name)

def generate_summary(text):
    input_ids = sum_tokenizer([text], return_tensors="pt", max_length=1024, truncation=True).input_ids
    output_ids = sum_model.generate(
        input_ids=input_ids,
        num_beams=4,
        max_length=200,
        min_length=30,
        repetition_penalty=1.2,
        early_stopping=True
    )
    return sum_tokenizer.decode(output_ids[0], skip_special_tokens=True)

# --- Sentiment model (русский) ---
sentiment_pipeline = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment")

def detect_sentiment(text):
    result = sentiment_pipeline(text[:512])[0]
    return result['label'].lower()

# --- Tone classifier ---
tone_labels = ["факт", "аналитика", "мнение", "интервью", "расследование"]
tone_pipeline = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")

def detect_tone(text):
    result = tone_pipeline(text[:512], tone_labels)
    return result["labels"][0]

# --- Named Entity Recognition ---
ner_pipeline = pipeline("ner", model="Davlan/xlm-roberta-base-ner-hrl", aggregation_strategy="simple")

zero_shot = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")

CATEGORY_LABELS = [
    "политика",
    "экономика",
    "бизнес",
    "технологии",
    "спорт",
    "общество",
    "происшествия",
    "культура",
    "наука",
    "авто",
    "медиа",
    "здоровье",
    "путешествия"
]

SUBCATEGORY_LABELS = {
    "политика": [
        "выборы", "санкции", "коррупция", "международные отношения", "госуправление", "законопроекты", "военные конфликты"
    ],
    "экономика": [
        "инфляция", "безработица", "налоги", "бюджет", "валюта", "госдолг", "макроэкономика"
    ],
    "бизнес": [
        "рынки", "сделки", "финансовая отчётность", "IPO", "корпорации", "предпринимательство", "банковский сектор"
    ],
    "технологии": [
        "искусственный интеллект", "стартапы", "гаджеты", "кибербезопасность", "социальные сети", "блокчейн", "робототехника"
    ],
    "спорт": [
        "футбол", "олимпийские игры", "теннис", "хоккей", "трансферы", "чемпионаты", "рекорды"
    ],
    "общество": [
        "образование", "миграция", "семья", "трудоустройство", "социальная политика", "молодёжь", "демография"
    ],
    "происшествия": [
        "пожары", "ДТП", "преступления", "наводнения", "теракты", "взрывы", "катастрофы"
    ],
    "культура": [
        "кино", "литература", "театр", "музыка", "живопись", "фестивали", "музеи"
    ],
    "наука": [
        "астрофизика", "биология", "медицина", "экология", "инновации", "исследования", "технологические открытия"
    ],
    "авто": [
        "электромобили", "дорожные тесты", "новые модели", "аварии", "автосалон", "тюнинг", "грузовики"
    ],
    "медиа": [
        "телевидение", "интернет-СМИ", "журналистика", "цензура", "социальные медиа", "трансляции", "инфлюенсеры"
    ],
    "здоровье": [
        "психология", "заболевания", "лекарства", "здоровый образ жизни", "медицина", "эпидемии", "медуслуги"
    ],
    "путешествия": [
        "туризм", "авиаперелёты", "отели", "визы", "круизы", "гиды", "страны и города"
    ]
}

def classify_category(text):
    result = zero_shot(text[:1000], candidate_labels=CATEGORY_LABELS)
    return result["labels"][0]

def classify_subtopics(text, category):
    candidates = SUBCATEGORY_LABELS.get(category, [])
    if not candidates:
        return []
    result = zero_shot(text[:1000], candidate_labels=candidates, multi_label=True)
    return [label for label, score in zip(result['labels'], result['scores']) if score > 0.4]

def extract_named_entities(text):
    ents = ner_pipeline(text[:1000])
    people, orgs, locs = set(), set(), set()
    for ent in ents:
        if ent['entity_group'] == 'PER':
            people.add(ent['word'])
        elif ent['entity_group'] == 'ORG':
            orgs.add(ent['word'])
        elif ent['entity_group'] == 'LOC':
            locs.add(ent['word'])
    return {
        "persons": list(people),
        "orgs": list(orgs),
        "locations": list(locs)
    }

def parse(data: list[dict]) -> list[dict]:
    for val in tqdm(data):
        if len(val["text"]) < 10:
            if len(val["title"]) < 10:
                val["summary"] = None
                val["sentiment"] = None
                val["tone"] = None
                val["named_entities"] = None
                val["category"] = None
                val["subtopics"] = None
                continue
            val["summary"] = generate_summary(val["title"])
            val["sentiment"] = detect_sentiment(val["title"])
            val["tone"] = detect_tone(val["title"])
            val["named_entities"] = extract_named_entities(val["title"])
            val["category"] = classify_category(val["title"])
            val["subtopics"] = classify_subtopics(val["title"], val["category"])
            continue
        text = val["text"]
        val["summary"] = generate_summary(text)
        val["sentiment"] = detect_sentiment(text)
        val["tone"] = detect_tone(text)
        val["named_entities"] = extract_named_entities(text)
        val["category"] = classify_category(text)
        val["subtopics"] = classify_subtopics(text, val["category"])
    return data