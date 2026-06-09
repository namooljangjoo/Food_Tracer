import os
from dotenv import load_dotenv
from openai import OpenAI

from database import TranslationCache, SessionLocal

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


COMMON_TRANSLATIONS = {
    ("egg", "fa"): "تخم مرغ",
    ("rice", "fa"): "برنج",
    ("chicken breast", "fa"): "سینه مرغ",
    ("butter", "fa"): "کره",
    ("barbari bread", "fa"): "نان بربری",
    ("sangak bread", "fa"): "نان سنگک",
    ("lavash bread", "fa"): "نان لواش",
    ("bread", "fa"): "نان",
    ("strawberry jam", "fa"): "مربای توت‌فرنگی",
    ("jam", "fa"): "مربا",
    ("honey", "fa"): "عسل",
    ("milk", "fa"): "شیر",
    ("banana", "fa"): "موز",
    ("apple", "fa"): "سیب",
    ("whey protein", "fa"): "پروتئین وی",
    ("protein powder", "fa"): "پودر پروتئین",
    ("tuna", "fa"): "تن ماهی",
    ("oats", "fa"): "جو دوسر",
}


def get_cached_translation(source_text, language):
    db = SessionLocal()

    item = db.query(TranslationCache).filter(
        TranslationCache.source_text == source_text.lower().strip(),
        TranslationCache.language == language,
    ).first()

    db.close()
    return item


def save_translation(source_text, language, translated_text):
    db = SessionLocal()

    existing = db.query(TranslationCache).filter(
        TranslationCache.source_text == source_text.lower().strip(),
        TranslationCache.language == language,
    ).first()

    if existing:
        existing.translated_text = translated_text
    else:
        item = TranslationCache(
            source_text=source_text.lower().strip(),
            language=language,
            translated_text=translated_text,
        )
        db.add(item)

    db.commit()
    db.close()


def translate_food_name(food_name, language):
    food_key = food_name.lower().strip()

    if language == "en":
        return food_name

    if (food_key, language) in COMMON_TRANSLATIONS:
        return COMMON_TRANSLATIONS[(food_key, language)]

    cached = get_cached_translation(food_key, language)

    if cached:
        return cached.translated_text

    prompt = f"""
Translate this food name to Persian.
Return only the translated food name.
Food: {food_name}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    translated = response.choices[0].message.content.strip()
    save_translation(food_key, language, translated)
    return translated
