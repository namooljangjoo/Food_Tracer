from nutrition_api import get_food_nutrition
from unit_converter import convert_to_grams


def calculate_food(food, quantity, unit):
    nutrition = get_food_nutrition(food)

    if not nutrition:
        print("NUTRITION NOT FOUND:", food)
        return None

    grams = convert_to_grams(food, quantity, unit)

    if not grams:
        print("UNIT NOT FOUND:", food, quantity, unit)
        return None

    calories = nutrition["calories_per_100g"] * grams / 100
    protein = nutrition["protein_per_100g"] * grams / 100

    return {
        "food": nutrition["food"],
        "grams": grams,
        "calories": round(calories, 1),
        "protein": round(protein, 1),
    }
