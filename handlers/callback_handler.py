from datetime import date, timedelta

from telegram import Update
from telegram.ext import ContextTypes

from calendar_service import build_calendar
from history_formatter import format_history
from history_service import get_history_range
from settings_service import get_language


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = get_language(user_id) or "fa"
    data = query.data
    today_date = date.today()

    if data == "ignore":
        return

    if data == "hist:cancel":
        await query.edit_message_text("Cancelled." if language == "en" else "لغو شد.")
        return

    if data == "hist:today":
        history_data = get_history_range(user_id, today_date, today_date)

    elif data == "hist:yesterday":
        yesterday = today_date - timedelta(days=1)
        history_data = get_history_range(user_id, yesterday, yesterday)

    elif data == "hist:last7":
        start = today_date - timedelta(days=6)
        history_data = get_history_range(user_id, start, today_date)

    elif data == "hist:last30":
        start = today_date - timedelta(days=29)
        history_data = get_history_range(user_id, start, today_date)

    elif data == "hist:custom":
        text = "📅 Choose start date:" if language == "en" else "📅 تاریخ شروع را انتخاب کن:"
        await query.edit_message_text(text, reply_markup=build_calendar(purpose="start"))
        return

    elif data.startswith("cal:"):
        _, purpose, year, month, action = data.split(":")
        year = int(year)
        month = int(month)

        if action == "prev":
            month -= 1
            if month == 0:
                month = 12
                year -= 1

        elif action == "next":
            month += 1
            if month == 13:
                month = 1
                year += 1

        await query.edit_message_reply_markup(reply_markup=build_calendar(year, month, purpose))
        return

    elif data.startswith("date:"):
        _, purpose, selected_date = data.split(":")
        selected = date.fromisoformat(selected_date)

        if purpose == "start":
            context.user_data["history_start"] = selected
            text = "📅 Choose end date:" if language == "en" else "📅 تاریخ پایان را انتخاب کن:"
            await query.edit_message_text(text, reply_markup=build_calendar(purpose="end"))
            return

        if purpose == "end":
            start = context.user_data.get("history_start")
            end = selected

            if not start:
                text = "Please try again." if language == "en" else "لطفاً دوباره تلاش کن."
                await query.edit_message_text(text)
                return

            if start > end:
                text = "Start date cannot be after end date." if language == "en" else "تاریخ شروع نباید بعد از تاریخ پایان باشد."
                await query.edit_message_text(text)
                return

            history_data = get_history_range(user_id, start, end)
    else:
        return

    text = format_history(history_data, language)
    await query.edit_message_text(text)
