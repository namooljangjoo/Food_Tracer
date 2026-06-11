from telegram import Update
from telegram.ext import ContextTypes

from meal_plan_service import generate_weekly_meal_plan
from menu_service import reports_keyboard
from settings_service import get_language


async def weekly_meal_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"

    await update.message.reply_text(
        "🍱 در حال ساخت برنامه غذایی هفتگی..."
        if language == "fa"
        else "🍱 Creating your weekly meal plan..."
    )

    try:
        plan = generate_weekly_meal_plan(user_id, language)

        if not plan:
            await update.message.reply_text(
                "اول هدف روزانه‌ات را تنظیم کن."
                if language == "fa"
                else "Please set your daily goal first.",
                reply_markup=reports_keyboard(language),
            )
            return

        await update.message.reply_text(
            plan,
            reply_markup=reports_keyboard(language),
        )

    except Exception as e:
        print("MEAL PLAN ERROR:", repr(e), flush=True)

        await update.message.reply_text(
            "نتونستم برنامه غذایی بسازم."
            if language == "fa"
            else "I couldn't create a meal plan.",
            reply_markup=reports_keyboard(language),
        )
