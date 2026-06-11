from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes

from goals_service import save_goal, get_goal
from settings_service import save_language, get_language
from streak_service import get_streak
from menu_service import main_keyboard
from states import ASK_LANGUAGE, ASK_CALORIES, ASK_PROTEIN


def language_keyboard():
    return ReplyKeyboardMarkup(
        [["فارسی", "English"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id)

    if not language:
        context.user_data["changing_language_only"] = False
        await update.message.reply_text(
            "Please choose your language:\n\nلطفاً زبان خود را انتخاب کنید:",
            reply_markup=language_keyboard(),
        )
        return ASK_LANGUAGE

    goal = get_goal(user_id)

    if not goal:
        text = (
            "What is your daily calorie goal?\nExample: 2500"
            if language == "en"
            else "هدفت برای کالری روزانه چقدره؟\nمثلاً بنویس: 2500"
        )
        await update.message.reply_text(text, reply_markup=main_keyboard(language))
        return ASK_CALORIES

    streak = get_streak(user_id)

    text = (
        "Hi 👋\n\nEverything is ready. Just send what you ate."
        if language == "en"
        else "سلام 👋\n\nهمه چیز آماده است. هر غذایی خوردی فقط بنویس."
    )

    if language == "en":
        text += (
            f"\n\n🔥 Current Streak: {streak['current']} days"
            f"\n🏆 Best Streak: {streak['best']} days"
        )
    else:
        text += (
            f"\n\n🔥 استریک فعلی: {streak['current']} روز"
            f"\n🏆 بهترین رکورد: {streak['best']} روز"
        )

    await update.message.reply_text(text, reply_markup=main_keyboard(language))
    return ConversationHandler.END
async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["changing_language_only"] = True
    await update.message.reply_text(
        "Please choose your language:\n\nلطفاً زبان خود را انتخاب کنید:",
        reply_markup=language_keyboard(),
    )
    return ASK_LANGUAGE
async def ask_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if text == "فارسی":
        language = "fa"
    elif text == "English":
        language = "en"
    else:
        await update.message.reply_text(
            "Please choose one option.\nلطفاً یکی از گزینه‌ها را انتخاب کن."
        )
        return ASK_LANGUAGE

    save_language(user_id, language)

    changing_only = context.user_data.get("changing_language_only", False)
    goal = get_goal(user_id)

    if changing_only or goal:
        msg = "English selected ✅" if language == "en" else "زبان فارسی انتخاب شد ✅"
        await update.message.reply_text(msg, reply_markup=main_keyboard(language))
        return ConversationHandler.END

    text = (
        "English selected ✅\n\nWhat is your daily calorie goal?\nExample: 2500"
        if language == "en"
        else "زبان فارسی انتخاب شد ✅\n\nهدفت برای کالری روزانه چقدره؟\nمثلاً بنویس: 2500"
    )
    await update.message.reply_text(text, reply_markup=main_keyboard(language))
    return ASK_CALORIES
async def ask_calories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"

    try:
        calories = float(update.message.text.replace(",", "."))
        context.user_data["calories_goal"] = calories

        text = (
            "Great ✅\n\nWhat is your daily protein goal in grams?\nExample: 180"
            if language == "en"
            else "عالی ✅\n\nحالا هدف پروتئین روزانه‌ات چند گرمه؟\nمثلاً بنویس: 180"
        )

        await update.message.reply_text(text, reply_markup=main_keyboard(language))
        return ASK_PROTEIN

    except ValueError:
        text = (
            "Please enter only a number.\nExample: 2500"
            if language == "en"
            else "لطفاً فقط عدد وارد کن.\nمثلاً: 2500"
        )
        await update.message.reply_text(text)
        return ASK_CALORIES
async def ask_protein(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"

    try:
        protein = float(update.message.text.replace(",", "."))
        calories = context.user_data["calories_goal"]

        save_goal(user_id, calories, protein)

        if language == "en":
            text = (
                "✅ Daily goal saved:\n\n"
                f"🔥 Calories: {calories}\n"
                f"💪 Protein: {protein}g\n\n"
                "You can optionally log your current weight.\n"
                "If not now, use the ⚖️ Log weight button later.\n\n"
                "Now just send what you ate."
            )
        else:
            text = (
                "✅ هدف روزانه ذخیره شد:\n\n"
                f"🔥 کالری: {calories}\n"
                f"💪 پروتئین: {protein} گرم\n\n"
                "در صورت تمایل می‌تونی وزن فعلی‌ات رو هم ثبت کنی.\n"
                "اگر الان نمی‌خوای، بعداً از دکمه ⚖️ ثبت وزن استفاده کن.\n\n"
                "از حالا هر غذایی خوردی فقط بنویس."
            )

        await update.message.reply_text(text, reply_markup=main_keyboard(language))
        return ConversationHandler.END

    except ValueError:
        text = (
            "Please enter only a number.\nExample: 180"
            if language == "en"
            else "لطفاً فقط عدد وارد کن.\nمثلاً: 180"
        )
        await update.message.reply_text(text)
        return ASK_PROTEIN
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = get_language(update.effective_user.id) or "fa"
    text = "Cancelled." if language == "en" else "لغو شد."
    await update.message.reply_text(text, reply_markup=main_keyboard(language))
    return ConversationHandler.END
