from datetime import date
from database import FoodLog, SessionLocal
from goals_service import get_goal


def get_today_summary(user_id):
    db = SessionLocal()

    logs = db.query(FoodLog).filter(
        FoodLog.user_id == user_id,
        FoodLog.log_date == date.today()
    ).all()

    total_calories = sum(item.calories for item in logs)
    total_protein = sum(item.protein for item in logs)
    goal = get_goal(user_id)

    db.close()

    result = {
        "total_calories": round(total_calories, 1),
        "total_protein": round(total_protein, 1),
        "items_count": len(logs),
    }

    if goal:
        result["calories_goal"] = goal.calories_goal
        result["protein_goal"] = goal.protein_goal
        result["remaining_calories"] = round(goal.calories_goal - total_calories, 1)
        result["remaining_protein"] = round(goal.protein_goal - total_protein, 1)

    return result


def get_today_foods(user_id):
    db = SessionLocal()

    logs = db.query(FoodLog).filter(
        FoodLog.user_id == user_id,
        FoodLog.log_date == date.today()
    ).order_by(FoodLog.id.asc()).all()

    result = [
        {
            "id": log.id,
            "meal_id": log.meal_id,
            "food_name": log.food_name,
            "calories": log.calories,
            "protein": log.protein,
        }
        for log in logs
    ]

    db.close()
    return result


def undo_last_meal(user_id):
    db = SessionLocal()

    last_log = db.query(FoodLog).filter(
        FoodLog.user_id == user_id,
        FoodLog.log_date == date.today()
    ).order_by(FoodLog.id.desc()).first()

    if not last_log:
        db.close()
        return None

    meal_id = last_log.meal_id

    logs = db.query(FoodLog).filter(
        FoodLog.user_id == user_id,
        FoodLog.meal_id == meal_id
    ).all()

    deleted_items = []

    for log in logs:
        deleted_items.append({
            "food_name": log.food_name,
            "calories": log.calories,
            "protein": log.protein,
        })
        db.delete(log)

    db.commit()
    db.close()

    return deleted_items


def clear_today_foods(user_id):
    db = SessionLocal()

    logs = db.query(FoodLog).filter(
        FoodLog.user_id == user_id,
        FoodLog.log_date == date.today()
    ).all()

    deleted_count = len(logs)

    for log in logs:
        db.delete(log)

    db.commit()
    db.close()

    return deleted_count
