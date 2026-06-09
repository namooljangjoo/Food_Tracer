from datetime import date, timedelta

from database import WeightLog, SessionLocal


def save_weight(user_id, weight):
    db = SessionLocal()
    today = date.today()

    existing = db.query(WeightLog).filter(
        WeightLog.user_id == user_id,
        WeightLog.log_date == today
    ).first()

    if existing:
        existing.weight = weight
    else:
        log = WeightLog(
            user_id=user_id,
            weight=weight,
            log_date=today
        )
        db.add(log)

    db.commit()
    db.close()


def get_latest_weight(user_id):
    db = SessionLocal()

    log = db.query(WeightLog).filter(
        WeightLog.user_id == user_id
    ).order_by(WeightLog.log_date.desc()).first()

    db.close()
    return log


def get_weight_history(user_id, days=30):
    db = SessionLocal()
    start_date = date.today() - timedelta(days=days - 1)

    logs = db.query(WeightLog).filter(
        WeightLog.user_id == user_id,
        WeightLog.log_date >= start_date
    ).order_by(WeightLog.log_date.asc()).all()

    result = [{"date": str(log.log_date), "weight": log.weight} for log in logs]
    db.close()
    return result
