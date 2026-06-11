from telegram import Update
from telegram.ext import ContextTypes

from goals_service import save_goal
from menu_service import main_keyboard
from settings_service import get_language


async def goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"

    try:
        calories = float(context.args[0].replace(",", "."))
        protein = float(context.args[1].replace(",", "."))
        save_goal(user_id, calories, protein)

        text = (
            f"✅ Daily goal saved:\n\n🔥 Calories: {calories}\n💪 Protein: {protein}g"
            if language == "en"
            else f"✅ هدف روزانه ذخیره شد:\n\n🔥 کالری: {calories}\n💪 پروتئین: {protein} گرم"
        )
        await update.message.reply_text(text, reply_markup=main_keyboard(language))

    except Exception:
        text = (
            "Correct format:\n/goal 2500 180"
            if language == "en"
            else "فرمت درست:\n/goal 2500 180"
        )
        await update.message.reply_text(text)
