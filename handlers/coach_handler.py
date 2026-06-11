from telegram import Update
from telegram.ext import ContextTypes

from ai_coach_service import generate_ai_coach_report
from coach_data_service import build_coach_data, get_coach_cooldown, mark_coach_used
from menu_service import reports_keyboard
from settings_service import get_language


async def ai_coach_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"
    cooldown = get_coach_cooldown(user_id)

    if cooldown:
        hours = int(cooldown.total_seconds() // 3600)
        minutes = int((cooldown.total_seconds() % 3600) // 60)
        await update.message.reply_text(
            f"برای استفاده دوباره حدود {hours} ساعت و {minutes} دقیقه صبر کن."
            if language == "fa"
            else f"Please wait about {hours}h {minutes}m before using this again.",
            reply_markup=reports_keyboard(language),
        )
        return

    await update.message.reply_text(
        "🧠 در حال تحلیل داده‌ها..."
        if language == "fa"
        else
        "🧠 Analyzing your nutrition..."
    )

    try:
        profile, weekly, foods = build_coach_data(user_id)

        report = generate_ai_coach_report(
            profile,
            weekly,
            foods,
        )

        mark_coach_used(user_id)

        await update.message.reply_text(
            report,
            reply_markup=reports_keyboard(language),
        )

    except Exception as e:
        print("AI COACH ERROR:", repr(e), flush=True)

        await update.message.reply_text(
            "نتونستم تحلیل را تولید کنم."
            if language == "fa"
            else
            "I couldn't generate the analysis.",
            reply_markup=reports_keyboard(language),
        )

    return

