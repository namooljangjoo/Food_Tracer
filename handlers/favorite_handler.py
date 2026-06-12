from telegram import Update
from telegram.ext import ContextTypes

from analytics_service import track_event
from favorites_service import save_favorite, get_favorites
from settings_service import get_language


def normalize_favorite_number(text):
    text = text.strip()

    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"

    for p, e in zip(persian_digits, english_digits):
        text = text.replace(p, e)

    text = text.replace("⭐", "")
    text = text.replace("*", "")
    text = text.strip()

    if text.isdigit():
        return int(text)

    return None


async def handle_favorite_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    language = get_language(user_id) or "fa"
    title = text

    save_favorite(
        user_id,
        title,
        context.user_data["last_food_text"],
    )
    track_event(user_id, "favorite_saved")

    context.user_data["awaiting_favorite_name"] = False

    await update.message.reply_text(
        "✅ ذخیره شد."
        if language == "fa"
        else "✅ Saved."
    )
    return

async def start_save_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = get_language(update.effective_user.id) or "fa"
    last_food = context.user_data.get("last_food_text")

    if not last_food:
        await update.message.reply_text(
            "اول یک غذا ثبت کن."
            if language == "fa"
            else "Log a food first."
        )
        return

    context.user_data["awaiting_favorite_name"] = True

    await update.message.reply_text(
        "اسم میانبر را وارد کن:"
        if language == "fa"
        else "Enter favorite name:"
    )
    return

async def list_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"
    favorites = get_favorites(user_id)

    if not favorites:
        await update.message.reply_text(
            "موردی ثبت نشده."
            if language == "fa"
            else "No favorites yet."
        )
        return

    message = "⭐ غذاهای محبوب\n\n" if language == "fa" else "⭐ Favorites\n\n"

    for item in favorites:
        message += f"{item.id}. {item.title}\n"

    message += (
        "\nبرای ثبت بنویس:\n⭐ 1"
        if language == "fa"
        else
        "\nTo log write:\n⭐ 1"
    )

    await update.message.reply_text(message)
    return
