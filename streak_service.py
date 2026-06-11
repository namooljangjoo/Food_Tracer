from datetime import date, timedelta

from database import SessionLocal, UserStats


def update_streak(user_id):
    db = SessionLocal()

    stats = (
        db.query(UserStats)
        .filter(UserStats.user_id == user_id)
        .first()
    )

    today = date.today()

    if not stats:
        stats = UserStats(
            user_id=user_id,
            current_streak=1,
            best_streak=1,
            last_log_date=today,
        )

        db.add(stats)
        db.commit()
        db.close()

        return {
            "current": 1,
            "best": 1,
            "new_day": True,
        }

    if stats.last_log_date == today:
        result = {
            "current": stats.current_streak,
            "best": stats.best_streak,
            "new_day": False,
        }

        db.close()
        return result

    yesterday = today - timedelta(days=1)

    if stats.last_log_date == yesterday:
        stats.current_streak += 1
    else:
        stats.current_streak = 1

    if stats.current_streak > stats.best_streak:
        stats.best_streak = stats.current_streak

    stats.last_log_date = today

    db.commit()

    result = {
        "current": stats.current_streak,
        "best": stats.best_streak,
        "new_day": True,
    }

    db.close()

    return result


def get_streak(user_id):
    db = SessionLocal()

    stats = (
        db.query(UserStats)
        .filter(UserStats.user_id == user_id)
        .first()
    )

    db.close()

    if not stats:
        return {
            "current": 0,
            "best": 0,
        }

    return {
        "current": stats.current_streak,
        "best": stats.best_streak,
    }
