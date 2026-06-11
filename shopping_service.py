from collections import Counter
from datetime import date, timedelta

from database import FoodLog, SessionLocal


def _estimate_weekly_amount(food_name, count):
    food = food_name.lower().strip()

    rules = [
        (["egg"], "عدد", 2),
        (["banana"], "عدد", 1),
        (["apple"], "عدد", 1),
        (["orange"], "عدد", 1),
        (["chicken", "chicken breast"], "کیلو", 0.2),
        (["tuna"], "قوطی", 1),
        (["milk"], "لیتر", 0.25),
        (["yogurt", "ماست"], "کیلو", 0.2),
        (["rice", "برنج"], "کیلو", 0.1),
        (["bread", "نان"], "عدد/برش", 1),
        (["oats"], "کیلو", 0.08),
        (["protein powder", "whey"], "اسکوپ", 1),
    ]

    for keywords, unit, per_use in rules:
        if any(keyword in food for keyword in keywords):
            amount = count * per_use

            if unit == "کیلو":
                return f"{round(amount, 1)} کیلو"

            if unit == "لیتر":
                return f"{round(amount, 1)} لیتر"

            return f"{round(amount)} {unit}"

    return None


def generate_shopping_list(user_id, days=30):
    db = SessionLocal()

    start_date = date.today() - timedelta(days=days)

    foods = (
        db.query(FoodLog)
        .filter(
            FoodLog.user_id == user_id,
            FoodLog.log_date >= start_date,
        )
        .all()
    )

    db.close()

    if not foods:
        return []

    counter = Counter()

    for food in foods:
        counter[food.food_name] += 1

    return counter.most_common(20)


def generate_weekly_shopping_list(user_id):
    monthly_items = generate_shopping_list(user_id, days=30)

    result = []

    for food_name, monthly_count in monthly_items:
        weekly_count = max(1, round(monthly_count * 7 / 30))
        amount = _estimate_weekly_amount(food_name, weekly_count)

        result.append({
            "food_name": food_name,
            "monthly_count": monthly_count,
            "weekly_count": weekly_count,
            "amount": amount,
        })

    return result
