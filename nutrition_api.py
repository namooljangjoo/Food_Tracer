import os
import requests
from dotenv import load_dotenv
from cache_service import get_cached_food, save_cached_food

load_dotenv()

USDA_API_KEY = os.getenv("USDA_API_KEY")

COMMON_FOODS = {
    "egg": {"description": "egg", "calories_per_100g": 143, "protein_per_100g": 12.6},
    "rice": {"description": "white rice cooked", "calories_per_100g": 130, "protein_per_100g": 2.7},
    "chicken breast": {"description": "chicken breast cooked", "calories_per_100g": 165, "protein_per_100g": 31},
    "butter": {"description": "butter", "calories_per_100g": 717, "protein_per_100g": 0.9},
    "barbari bread": {"description": "barbari bread", "calories_per_100g": 270, "protein_per_100g": 8.5},
    "sangak bread": {"description": "sangak bread", "calories_per_100g": 260, "protein_per_100g": 8.7},
    "lavash bread": {"description": "lavash bread", "calories_per_100g": 275, "protein_per_100g": 9},
    "bread": {"description": "bread", "calories_per_100g": 265, "protein_per_100g": 9},
    "strawberry jam": {"description": "strawberry jam", "calories_per_100g": 250, "protein_per_100g": 0.4},
    "jam": {"description": "jam", "calories_per_100g": 250, "protein_per_100g": 0.4},
    "honey": {"description": "honey", "calories_per_100g": 304, "protein_per_100g": 0.3},
    "milk": {"description": "milk", "calories_per_100g": 61, "protein_per_100g": 3.3},
    "banana": {"description": "banana", "calories_per_100g": 89, "protein_per_100g": 1.1},
    "apple": {"description": "apple", "calories_per_100g": 52, "protein_per_100g": 0.3},
    "whey protein": {"description": "whey protein powder", "calories_per_100g": 400, "protein_per_100g": 80},
    "protein powder": {"description": "protein powder", "calories_per_100g": 400, "protein_per_100g": 80},
    "tuna": {"description": "tuna canned", "calories_per_100g": 132, "protein_per_100g": 28},
    "oats": {"description": "oats", "calories_per_100g": 389, "protein_per_100g": 16.9},
}


def normalize_food_name(food_name):
    food = food_name.lower().strip()

    mapping = {
        "barbari": "barbari bread",
        "barbari naan": "barbari bread",
        "naan barbari": "barbari bread",
        "nan barbari": "barbari bread",
        "persian barbari bread": "barbari bread",

        "sangak": "sangak bread",
        "sangak naan": "sangak bread",
        "naan sangak": "sangak bread",

        "lavash": "lavash bread",
        "lavash naan": "lavash bread",

        "strawberry preserve": "strawberry jam",
        "strawberry preserves": "strawberry jam",

        "chicken": "chicken breast",
        "chicken fillet": "chicken breast",

        "protein": "whey protein",
        "whey": "whey protein",
    }

    return mapping.get(food, food)


def get_food_nutrition(food_name):
    food_key = normalize_food_name(food_name)

    cached = get_cached_food(food_key)
    if cached:
        return {
            "food": food_key,
            "description": "cached",
            "calories_per_100g": cached.calories_per_100g,
            "protein_per_100g": cached.protein_per_100g,
        }

    if food_key in COMMON_FOODS:
        data = COMMON_FOODS[food_key]
        save_cached_food(food_key, data["calories_per_100g"], data["protein_per_100g"])
        return {"food": food_key, **data}

    url = "https://api.nal.usda.gov/fdc/v1/foods/search"

    params = {
        "api_key": USDA_API_KEY,
        "query": food_key,
        "pageSize": 1,
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()

    if not data.get("foods"):
        return None

    food = data["foods"][0]

    calories = 0
    protein = 0

    for nutrient in food.get("foodNutrients", []):
        name = nutrient.get("nutrientName", "").lower()
        value = nutrient.get("value", 0)

        if "energy" in name:
            calories = value

        if "protein" in name:
            protein = value

    save_cached_food(food_key, calories, protein)

    return {
        "food": food_key,
        "description": food.get("description"),
        "calories_per_100g": calories,
        "protein_per_100g": protein,
    }
