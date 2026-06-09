def format_analysis(analysis, language="fa"):
    if language == "en":
        return format_analysis_en(analysis)
    return format_analysis_fa(analysis)


def format_analysis_fa(a):
    lines = ["🧠 تحلیل تغذیه", "", "📅 بازه: ۷ روز اخیر", ""]

    lines.append(f"📌 روزهای ثبت‌شده: {a['logged_days']} / 7")

    if a["latest_weight"]:
        lines.append(f"⚖️ آخرین وزن: {a['latest_weight']} kg")

    lines.append("")
    lines.append(f"🔥 میانگین کالری: {a['avg_calories']}")

    if a["calories_goal"]:
        lines.append(f"🎯 هدف کالری: {a['calories_goal']}")
        lines.append(f"📊 درصد رسیدن به هدف کالری: {a['calories_achievement']}%")

        if a["calories_status"] == "on_target":
            lines.append("🟢 کالری تقریباً مطابق هدف است.")
        elif a["calories_status"] == "low":
            lines.append(f"🟡 کالری کمتر از هدف است: {abs(a['calories_diff'])} کالری پایین‌تر.")
        elif a["calories_status"] == "high":
            lines.append(f"🟡 کالری بیشتر از هدف است: {a['calories_diff']} کالری بالاتر.")

    lines.append("")
    lines.append(f"💪 میانگین پروتئین: {a['avg_protein']} گرم")

    if a["protein_goal"]:
        lines.append(f"🎯 هدف پروتئین: {a['protein_goal']} گرم")
        lines.append(f"📊 درصد رسیدن به هدف پروتئین: {a['protein_achievement']}%")

        if a["protein_status"] == "good":
            lines.append("🟢 پروتئین خوب است.")
        elif a["protein_status"] == "moderate":
            lines.append(f"🟡 پروتئین کمی پایین است: {abs(a['protein_diff'])} گرم کمتر از هدف.")
        elif a["protein_status"] == "low":
            lines.append(f"🔴 پروتئین خیلی پایین است: {abs(a['protein_diff'])} گرم کمتر از هدف.")

    lines.append("")
    lines.append("💡 پیشنهادها:")

    suggestions = set(a["suggestions"])

    if not suggestions:
        lines.append("✅ روند کلی خوب است. همین مسیر را ادامه بده.")
    else:
        if "increase_protein" in suggestions:
            lines.append("- برای افزایش پروتئین: ۱۵۰ گرم مرغ، ۲ تخم‌مرغ، یک قوطی تن یا یک اسکوپ وی اضافه کن.")
        if "increase_calories" in suggestions:
            lines.append("- اگر انرژی کم داری، کمی کربوهیدرات یا چربی سالم اضافه کن.")
        if "reduce_calories" in suggestions:
            lines.append("- اگر هدف کاهش وزن است، از خوراکی‌های پرکالری کوچک مثل کره، آجیل و شیرینی بیشتر مراقبت کن.")
        if "log_more_days" in suggestions:
            lines.append("- حداقل ۵ روز در هفته ثبت غذا داشته باش تا تحلیل دقیق‌تر شود.")

    return "\n".join(lines)


def format_analysis_en(a):
    lines = ["🧠 Nutrition Analysis", "", "📅 Range: Last 7 days", ""]

    lines.append(f"📌 Logged days: {a['logged_days']} / 7")

    if a["latest_weight"]:
        lines.append(f"⚖️ Latest weight: {a['latest_weight']} kg")

    lines.append("")
    lines.append(f"🔥 Average calories: {a['avg_calories']}")

    if a["calories_goal"]:
        lines.append(f"🎯 Calorie goal: {a['calories_goal']}")
        lines.append(f"📊 Calorie goal achievement: {a['calories_achievement']}%")

        if a["calories_status"] == "on_target":
            lines.append("🟢 Calories are close to target.")
        elif a["calories_status"] == "low":
            lines.append(f"🟡 Calories are below target by {abs(a['calories_diff'])}.")
        elif a["calories_status"] == "high":
            lines.append(f"🟡 Calories are above target by {a['calories_diff']}.")

    lines.append("")
    lines.append(f"💪 Average protein: {a['avg_protein']}g")

    if a["protein_goal"]:
        lines.append(f"🎯 Protein goal: {a['protein_goal']}g")
        lines.append(f"📊 Protein goal achievement: {a['protein_achievement']}%")

        if a["protein_status"] == "good":
            lines.append("🟢 Protein intake is good.")
        elif a["protein_status"] == "moderate":
            lines.append(f"🟡 Protein is slightly low: {abs(a['protein_diff'])}g below target.")
        elif a["protein_status"] == "low":
            lines.append(f"🔴 Protein is too low: {abs(a['protein_diff'])}g below target.")

    lines.append("")
    lines.append("💡 Suggestions:")

    suggestions = set(a["suggestions"])

    if not suggestions:
        lines.append("✅ Overall trend looks good. Keep going.")
    else:
        if "increase_protein" in suggestions:
            lines.append("- Add protein: 150g chicken, 2 eggs, one tuna can, or one whey scoop.")
        if "increase_calories" in suggestions:
            lines.append("- If energy is low, add some carbs or healthy fats.")
        if "reduce_calories" in suggestions:
            lines.append("- If fat loss is the goal, watch calorie-dense foods like butter, nuts, and sweets.")
        if "log_more_days" in suggestions:
            lines.append("- Log food at least 5 days per week for a better analysis.")

    return "\n".join(lines)
