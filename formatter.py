from localization_service import translate_food_name


def format_meal_response(meal_result, today_summary, language="fa"):
    lines = []

    if language == "fa":
        lines.append("✅ غذا ثبت شد\n")

        for item in meal_result["items"]:
            food_name = translate_food_name(item["food"], language)
            lines.append(
                f"🍽 {food_name} | "
                f"{item['calories']} کالری | "
                f"{item['protein']} گرم پروتئین"
            )

        lines.append("")
        lines.append("📊 مجموع امروز")
        lines.append(f"🔥 کالری: {today_summary['total_calories']}")
        lines.append(f"💪 پروتئین: {today_summary['total_protein']} گرم")

        if "calories_goal" in today_summary:
            lines.append("")
            lines.append(f"🎯 هدف کالری: {today_summary['calories_goal']}")
            lines.append(f"🎯 هدف پروتئین: {today_summary['protein_goal']} گرم")
            lines.append("")
            lines.append(f"⌛ باقی‌مانده کالری: {today_summary['remaining_calories']}")
            lines.append(f"⌛ باقی‌مانده پروتئین: {today_summary['remaining_protein']} گرم")

        return "\n".join(lines)

    lines.append("✅ Food saved\n")

    for item in meal_result["items"]:
        lines.append(
            f"🍽 {item['food']} | "
            f"{item['calories']} kcal | "
            f"{item['protein']}g protein"
        )

    lines.append("")
    lines.append("📊 Today")
    lines.append(f"🔥 Calories: {today_summary['total_calories']}")
    lines.append(f"💪 Protein: {today_summary['total_protein']}g")

    if "calories_goal" in today_summary:
        lines.append("")
        lines.append(f"🎯 Calorie goal: {today_summary['calories_goal']}")
        lines.append(f"🎯 Protein goal: {today_summary['protein_goal']}g")
        lines.append("")
        lines.append(f"⌛ Remaining calories: {today_summary['remaining_calories']}")
        lines.append(f"⌛ Remaining protein: {today_summary['remaining_protein']}g")

    return "\n".join(lines)
