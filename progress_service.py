from daily_summary import get_today_summary


def make_progress_bar(percent, length=10):
    if percent < 0:
        percent = 0

    filled = round((percent / 100) * length)

    if filled > length:
        filled = length

    empty = length - filled

    return "█" * filled + "░" * empty


def get_today_progress(user_id):
    summary = get_today_summary(user_id)

    if "calories_goal" not in summary:
        return None

    calories_percent = round(
        (summary["total_calories"] / summary["calories_goal"]) * 100,
        1
    )

    protein_percent = round(
        (summary["total_protein"] / summary["protein_goal"]) * 100,
        1
    )

    return {
        "total_calories": summary["total_calories"],
        "calories_goal": summary["calories_goal"],
        "calories_percent": calories_percent,
        "calories_bar": make_progress_bar(calories_percent),

        "total_protein": summary["total_protein"],
        "protein_goal": summary["protein_goal"],
        "protein_percent": protein_percent,
        "protein_bar": make_progress_bar(protein_percent),
    }
