from datetime import date, timedelta, datetime

from database import FoodLog, SessionLocal


def parse_date(date_text):
    return datetime.strptime(date_text, "%Y-%m-%d").date()


def get_history_range(user_id, start_date=None, end_date=None):
    db = SessionLocal()

    if not end_date:
        end_date = date.today()

    if not start_date:
        start_date = end_date - timedelta(days=6)

    results = []
    current_day = start_date

    while current_day <= end_date:
        logs = db.query(FoodLog).filter(
            FoodLog.user_id == user_id,
            FoodLog.log_date == current_day
        ).all()

        calories = round(sum(item.calories for item in logs), 1)
        protein = round(sum(item.protein for item in logs), 1)

        results.append({
            "date": str(current_day),
            "calories": calories,
            "protein": protein,
            "has_data": len(logs) > 0,
        })

        current_day += timedelta(days=1)

    db.close()
    return results
