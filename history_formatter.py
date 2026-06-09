def format_history(history, language="fa"):
    lines = []
    has_any_data = any(day["has_data"] for day in history)

    start_date = history[0]["date"]
    end_date = history[-1]["date"]

    if language == "fa":
        lines.append(f"📅 تاریخچه از {start_date} تا {end_date}\n")

        if not has_any_data:
            lines.append("در این بازه هیچ غذایی ثبت نشده.")
            return "\n".join(lines)

        for day in history:
            if day["has_data"]:
                lines.append(
                    f"📆 {day['date']}\n"
                    f"🔥 {day['calories']} کالری\n"
                    f"💪 {day['protein']} گرم پروتئین\n"
                )
            else:
                lines.append(f"📆 {day['date']}\nثبت نشده\n")

    else:
        lines.append(f"📅 History from {start_date} to {end_date}\n")

        if not has_any_data:
            lines.append("No food was logged in this date range.")
            return "\n".join(lines)

        for day in history:
            if day["has_data"]:
                lines.append(
                    f"📆 {day['date']}\n"
                    f"🔥 {day['calories']} kcal\n"
                    f"💪 {day['protein']}g protein\n"
                )
            else:
                lines.append(f"📆 {day['date']}\nNo records\n")

    return "\n".join(lines)
