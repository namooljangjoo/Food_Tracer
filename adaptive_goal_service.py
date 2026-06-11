from goals_service import get_goal, save_goal
from report_service import get_weekly_report


def get_adaptive_goal_suggestion(user_id):
    goal = get_goal(user_id)

    if not goal:
        return None

    report = get_weekly_report(user_id)

    avg_calories = report["average_calories"]
    avg_protein = report["average_protein"]
    logged_days = report["logged_days_count"]

    if logged_days < 4:
        return {
            "type": "not_enough_data",
            "logged_days": logged_days,
        }

    current_calories = goal.calories_goal
    current_protein = goal.protein_goal

    suggestion = None

    if avg_calories > current_calories + 300:
        suggestion = {
            "type": "raise_calories",
            "current_calories": current_calories,
            "suggested_calories": round(avg_calories - 100),
            "current_protein": current_protein,
            "suggested_protein": current_protein,
            "reason": "average intake is much higher than current goal",
        }

    elif avg_calories < current_calories - 300:
        suggestion = {
            "type": "lower_calories",
            "current_calories": current_calories,
            "suggested_calories": round(avg_calories + 100),
            "current_protein": current_protein,
            "suggested_protein": current_protein,
            "reason": "average intake is much lower than current goal",
        }

    elif avg_protein < current_protein - 30:
        suggestion = {
            "type": "adjust_protein",
            "current_calories": current_calories,
            "suggested_calories": current_calories,
            "current_protein": current_protein,
            "suggested_protein": round(avg_protein + 20),
            "reason": "protein goal may be too high for current pattern",
        }

    if not suggestion:
        return {
            "type": "no_change",
            "avg_calories": avg_calories,
            "avg_protein": avg_protein,
            "current_calories": current_calories,
            "current_protein": current_protein,
        }

    suggestion["avg_calories"] = avg_calories
    suggestion["avg_protein"] = avg_protein
    suggestion["logged_days"] = logged_days

    return suggestion


def apply_adaptive_goal(user_id, suggestion):
    save_goal(
        user_id,
        suggestion["suggested_calories"],
        suggestion["suggested_protein"],
    )
