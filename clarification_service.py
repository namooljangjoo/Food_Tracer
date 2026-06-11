from telegram import ReplyKeyboardMarkup


APPROX_FA = "تقریبی حساب کن"
APPROX_EN = "Use estimate"


def normalize_food(food):
    return food.lower().strip()


def get_clarification(item, language="fa"):
    if item.get("_preference_applied"):
        return None

    food = normalize_food(item["food"])
    unit = item["unit"]

    rules = []

    if "egg" in food and unit == "piece":
        rules.append({
            "type": "egg_type",
            "question_fa": "تخم‌مرغ چطور بود؟",
            "question_en": "How was the egg prepared?",
            "options": [
                {"fa": "تخم‌مرغ آب‌پز متوسط", "en": "Medium boiled egg", "food": "boiled egg", "unit": "piece"},
                {"fa": "تخم‌مرغ نیمرو متوسط", "en": "Medium fried egg", "food": "fried egg", "unit": "piece"},
                {"fa": "تخم‌مرغ خام متوسط", "en": "Medium raw egg", "food": "egg", "unit": "piece"},
                {"fa": APPROX_FA, "en": APPROX_EN, "food": item["food"], "unit": item["unit"]},
            ],
        })

    if "bread" in food and unit in ["slice", "piece"]:
        rules.append({
            "type": "bread_type",
            "question_fa": "نوع نان کدام است؟",
            "question_en": "Which bread type?",
            "options": [
                {"fa": "نان تست", "en": "Toast bread", "food": "toast bread", "unit": "slice"},
                {"fa": "نان بربری", "en": "Barbari bread", "food": "barbari bread", "unit": "slice"},
                {"fa": "نان سنگک", "en": "Sangak bread", "food": "sangak bread", "unit": "slice"},
                {"fa": "نان لواش", "en": "Lavash bread", "food": "lavash bread", "unit": "piece"},
                {"fa": APPROX_FA, "en": APPROX_EN, "food": item["food"], "unit": item["unit"]},
            ],
        })

    if "milk" in food and unit in ["glass", "cup"]:
        rules.append({
            "type": "milk_type",
            "question_fa": "نوع شیر کدام است؟",
            "question_en": "Which milk type?",
            "options": [
                {"fa": "شیر کم‌چرب", "en": "Low fat milk", "food": "low fat milk", "unit": unit},
                {"fa": "شیر پرچرب", "en": "Whole milk", "food": "whole milk", "unit": unit},
                {"fa": "شیر ۳.۵ درصد", "en": "Milk 3.5% fat", "food": "milk 3.5% fat", "unit": unit},
                {"fa": APPROX_FA, "en": APPROX_EN, "food": item["food"], "unit": item["unit"]},
            ],
        })

    if "rice" in food and unit in ["plate", "cup"]:
        rules.append({
            "type": "rice_type",
            "question_fa": "برنج پخته بود یا خام؟",
            "question_en": "Was the rice cooked or dry?",
            "options": [
                {"fa": "برنج پخته", "en": "Cooked rice", "food": "cooked rice", "unit": unit},
                {"fa": "برنج خام", "en": "Dry rice", "food": "dry rice", "unit": unit},
                {"fa": APPROX_FA, "en": APPROX_EN, "food": item["food"], "unit": item["unit"]},
            ],
        })

    if any(x in food for x in ["oil", "olive oil", "butter"]) and unit in ["tablespoon", "teaspoon"]:
        rules.append({
            "type": "fat_type",
            "question_fa": "نوع چربی کدام است؟",
            "question_en": "Which fat type?",
            "options": [
                {"fa": "روغن زیتون", "en": "Olive oil", "food": "olive oil", "unit": unit},
                {"fa": "کره", "en": "Butter", "food": "butter", "unit": unit},
                {"fa": "روغن معمولی", "en": "Cooking oil", "food": "cooking oil", "unit": unit},
                {"fa": APPROX_FA, "en": APPROX_EN, "food": item["food"], "unit": item["unit"]},
            ],
        })

    if "cheese" in food and unit in ["slice", "piece"]:
        rules.append({
            "type": "cheese_type",
            "question_fa": "نوع پنیر کدام است؟",
            "question_en": "Which cheese type?",
            "options": [
                {"fa": "پنیر فتا", "en": "Feta cheese", "food": "feta cheese", "unit": unit},
                {"fa": "پنیر خامه‌ای", "en": "Cream cheese", "food": "cream cheese", "unit": unit},
                {"fa": "پنیر گودا", "en": "Gouda cheese", "food": "gouda cheese", "unit": unit},
                {"fa": APPROX_FA, "en": APPROX_EN, "food": item["food"], "unit": item["unit"]},
            ],
        })

    if not rules:
        return None

    rule = rules[0]
    rule["original_food"] = item["food"]
    labels = [opt["fa"] if language == "fa" else opt["en"] for opt in rule["options"]]

    return {
        "question": rule["question_fa"] if language == "fa" else rule["question_en"],
        "options": rule["options"],
        "original_food": item["food"],
        "keyboard": ReplyKeyboardMarkup(
            [[label] for label in labels],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    }


def find_next_clarification(parsed_foods, start_index=0, language="fa"):
    for index in range(start_index, len(parsed_foods)):
        clarification = get_clarification(parsed_foods[index], language)
        if clarification:
            return index, clarification

    return None, None


def apply_clarification(parsed_foods, item_index, selected_text, clarification, language="fa"):
    for option in clarification["options"]:
        label = option["fa"] if language == "fa" else option["en"]

        if selected_text == label:
            parsed_foods[item_index]["food"] = option["food"]
            parsed_foods[item_index]["unit"] = option["unit"]
            return parsed_foods

    return None
