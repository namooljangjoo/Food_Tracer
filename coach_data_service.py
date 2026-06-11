from datetime import datetime, timedelta

from database import CoachUsage, FoodLog, SessionLocal, WeightLog
from goals_service import get_goal
from report_service import get_weekly_report


COACH_COOLDOWN_HOURS = 6


def get_coach_cooldown(user_id):
    db = SessionLocal()

    usage = (
        db.query(CoachUsage)
        .filter(CoachUsage.user_id == user_id)
        .first()
    )

    db.close()

    if not usage or not usage.last_used_at:
        return None

    next_allowed_at = usage.last_used_at + timedelta(hours=COACH_COOLDOWN_HOURS)
    remaining = next_allowed_at - datetime.utcnow()

    if remaining.total_seconds() <= 0:
        return None

    return remaining


def mark_coach_used(user_id):
    db = SessionLocal()

    usage = (
        db.query(CoachUsage)
        .filter(CoachUsage.user_id == user_id)
        .first()
    )

    if usage:
        usage.last_used_at = datetime.utcnow()
    else:
        usage = CoachUsage(
            user_id=user_id,
            last_used_at=datetime.utcnow(),
        )
        db.add(usage)

    db.commit()
    db.close()


def build_coach_data(user_id):
    goal = get_goal(user_id)
    weekly = get_weekly_report(user_id)

    db = SessionLocal()

    recent_foods = (
        db.query(FoodLog)
        .filter(FoodLog.user_id == user_id)
        .order_by(FoodLog.log_date.desc(), FoodLog.id.desc())
        .limit(20)
        .all()
    )

    latest_weight = (
        db.query(WeightLog)
        .filter(WeightLog.user_id == user_id)
        .order_by(WeightLog.log_date.desc(), WeightLog.id.desc())
        .first()
    )

    db.close()

    foods_text = "\n".join(
        [
            f"{x.log_date} | {x.food_name} | {x.calories} kcal | {x.protein} protein"
            for x in recent_foods
        ]
    )

    profile = f"""
Current Weight: {latest_weight.weight if latest_weight else 'unknown'}

Calorie Goal: {goal.calories_goal if goal else 'unknown'}

Protein Goal: {goal.protein_goal if goal else 'unknown'}
"""

    return profile, weekly, foods_text or "No recent foods logged."
