from telegram import Update
from telegram.ext import ContextTypes

from history_formatter import format_history
from history_service import get_history_range
from menu_service import main_keyboard
from settings_service import get_language


async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"

    try:
        if len(context.args) == 2:
            from history_service import parse_date
            start_date = parse_date(context.args[0])
            end_date = parse_date(context.args[1])

            if start_date > end_date:
                text = "Start date cannot be after end date." if language == "en" else "تاریخ شروع نباید بعد از تاریخ پایان باشد."
                await update.message.reply_text(text)
                return
            history_data = get_history_range(user_id, start_date, end_date)
        else:
            history_data = get_history_range(user_id)

        text = format_history(history_data, language)
        await update.message.reply_text(text, reply_markup=main_keyboard(language))

    except Exception:
        text = (
            "Correct format:\n/history 2026-06-01 2026-06-08"
            if language == "en"
            else "فرمت درست:\n/history 2026-06-01 2026-06-08"
        )
        await update.message.reply_text(text)
