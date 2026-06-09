from report_service import get_weekly_report
from goals_service import get_goal
from weight_service import get_latest_weight


def analyze_nutrition(user_id):
    report = get_weekly_report(user_id)
    goal = get_goal(user_id)
    latest_weight = get_latest_weight(user_id)

    calories_goal = goal.calories_goal if goal else None
    protein_goal = goal.protein_goal if goal else None

    avg_calories = report["average_calories"]
    avg_protein = report["average_protein"]
    logged_days = report["logged_days_count"]

    result = {
        "avg_calories": avg_calories,
        "avg_protein": avg_protein,
        "logged_days": logged_days,
        "calories_goal": calories_goal,
        "protein_goal": protein_goal,
        "latest_weight": latest_weight.weight if latest_weight else None,
        "calories_diff": None,
        "protein_diff": None,
        "calories_achievement": None,
        "protein_achievement": None,
        "calories_status": "unknown",
        "protein_status": "unknown",
        "logging_status": "good" if logged_days >= 5 else "low",
        "suggestions": [],
    }

    if calories_goal:
        calories_diff = round(avg_calories - calories_goal, 1)
        calories_achievement = round((avg_calories / calories_goal) * 100, 1) if calories_goal else 0

        result["calories_diff"] = calories_diff
        result["calories_achievement"] = calories_achievement

        if abs(calories_diff) <= calories_goal * 0.1:
            result["calories_status"] = "on_target"
        elif calories_diff < 0:
            result["calories_status"] = "low"
            result["suggestions"].append("increase_calories")
        else:
            result["calories_status"] = "high"
            result["suggestions"].append("reduce_calories")

    if protein_goal:
        protein_diff = round(avg_protein - protein_goal, 1)
        protein_achievement = round((avg_protein / protein_goal) * 100, 1) if protein_goal else 0

        result["protein_diff"] = protein_diff
        result["protein_achievement"] = protein_achievement

        if protein_achievement >= 90:
            result["protein_status"] = "good"
        elif protein_achievement >= 70:
            result["protein_status"] = "moderate"
            result["suggestions"].append("increase_protein")
        else:
            result["protein_status"] = "low"
            result["suggestions"].append("increase_protein")

    if logged_days < 5:
        result["suggestions"].append("log_more_days")

    return result
