from datetime import date, timedelta
from database import FoodLog, SessionLocal
from weight_service import get_latest_weight


def get_weekly_report(user_id):
    db = SessionLocal()
    start_date = date.today() - timedelta(days=6)

    daily = {}

    for i in range(7):
        day = date.today() - timedelta(days=6 - i)
        daily[str(day)] = {"calories": 0, "protein": 0, "has_data": False}

    logs = db.query(FoodLog).filter(
        FoodLog.user_id == user_id,
        FoodLog.log_date >= start_date
    ).all()

    db.close()

    for log in logs:
        day = str(log.log_date)
        daily[day]["calories"] += log.calories
        daily[day]["protein"] += log.protein
        daily[day]["has_data"] = True

    logged_days = [v for v in daily.values() if v["has_data"]]
    logged_days_count = len(logged_days)

    if logged_days_count > 0:
        avg_calories = round(sum(v["calories"] for v in logged_days) / logged_days_count, 1)
        avg_protein = round(sum(v["protein"] for v in logged_days) / logged_days_count, 1)
    else:
        avg_calories = 0
        avg_protein = 0

    latest_weight = get_latest_weight(user_id)

    return {
        "daily": daily,
        "average_calories": avg_calories,
        "average_protein": avg_protein,
        "logged_days_count": logged_days_count,
        "latest_weight": latest_weight.weight if latest_weight else None,
    }
