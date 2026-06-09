from database import FoodCache, SessionLocal


def get_cached_food(food_name):
    db = SessionLocal()
    food_key = food_name.lower().strip()

    food = db.query(FoodCache).filter(
        FoodCache.food_name == food_key
    ).first()

    db.close()
    return food


def save_cached_food(food_name, calories_per_100g, protein_per_100g):
    db = SessionLocal()
    food_key = food_name.lower().strip()

    existing = db.query(FoodCache).filter(
        FoodCache.food_name == food_key
    ).first()

    if not existing:
        food = FoodCache(
            food_name=food_key,
            calories_per_100g=calories_per_100g,
            protein_per_100g=protein_per_100g,
        )
        db.add(food)
        db.commit()

    db.close()
