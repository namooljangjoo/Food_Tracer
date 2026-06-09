import calendar
from datetime import date
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_history_menu(language="fa"):
    if language == "en":
        keyboard = [
            [InlineKeyboardButton("Today", callback_data="hist:today")],
            [InlineKeyboardButton("Yesterday", callback_data="hist:yesterday")],
            [InlineKeyboardButton("Last 7 Days", callback_data="hist:last7")],
            [InlineKeyboardButton("Last 30 Days", callback_data="hist:last30")],
            [InlineKeyboardButton("Custom Range", callback_data="hist:custom")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("امروز", callback_data="hist:today")],
            [InlineKeyboardButton("دیروز", callback_data="hist:yesterday")],
            [InlineKeyboardButton("۷ روز اخیر", callback_data="hist:last7")],
            [InlineKeyboardButton("۳۰ روز اخیر", callback_data="hist:last30")],
            [InlineKeyboardButton("بازه دلخواه", callback_data="hist:custom")],
        ]

    return InlineKeyboardMarkup(keyboard)


def build_calendar(year=None, month=None, purpose="start"):
    today = date.today()

    if year is None:
        year = today.year

    if month is None:
        month = today.month

    month_name = calendar.month_name[month]
    keyboard = []

    keyboard.append([
        InlineKeyboardButton("◀️", callback_data=f"cal:{purpose}:{year}:{month}:prev"),
        InlineKeyboardButton(f"{month_name} {year}", callback_data="ignore"),
        InlineKeyboardButton("▶️", callback_data=f"cal:{purpose}:{year}:{month}:next"),
    ])

    keyboard.append([
        InlineKeyboardButton("Mo", callback_data="ignore"),
        InlineKeyboardButton("Tu", callback_data="ignore"),
        InlineKeyboardButton("We", callback_data="ignore"),
        InlineKeyboardButton("Th", callback_data="ignore"),
        InlineKeyboardButton("Fr", callback_data="ignore"),
        InlineKeyboardButton("Sa", callback_data="ignore"),
        InlineKeyboardButton("Su", callback_data="ignore"),
    ])

    month_calendar = calendar.monthcalendar(year, month)

    for week in month_calendar:
        row = []

        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data="ignore"))
            else:
                selected_date = date(year, month, day)
                row.append(
                    InlineKeyboardButton(
                        str(day),
                        callback_data=f"date:{purpose}:{selected_date}"
                    )
                )

        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="hist:cancel")])
    return InlineKeyboardMarkup(keyboard)
