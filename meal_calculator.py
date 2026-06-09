import uuid

from food_parser import parse_food
from calculator import calculate_food
from database import FoodLog, SessionLocal


def calculate_and_save_meal(text, user_id):
    parsed_foods = parse_food(text)
    meal_id = str(uuid.uuid4())

    db = SessionLocal()

    results = []
    total_calories = 0
    total_protein = 0

    for item in parsed_foods:
        result = calculate_food(
            item["food"],
            item["quantity"],
            item["unit"],
        )

        if result:
            food_log = FoodLog(
                user_id=user_id,
                meal_id=meal_id,
                food_name=result["food"],
                calories=result["calories"],
                protein=result["protein"],
            )

            db.add(food_log)

            results.append(result)
            total_calories += result["calories"]
            total_protein += result["protein"]

    db.commit()
    db.close()

    return {
        "meal_id": meal_id,
        "items": results,
        "total_calories": round(total_calories, 1),
        "total_protein": round(total_protein, 1),
    }
