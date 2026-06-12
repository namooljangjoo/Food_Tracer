from telegram import Update
from telegram.ext import ContextTypes

from admin_service import build_admin_report
from config import ADMIN_IDS


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Access denied.")
        return

    report = build_admin_report()

    text = (
        "📊 Admin Dashboard\n\n"
        f"👥 Total Users: {report['total_users']}\n"
        f"🔥 Active Today: {report['active_today']}\n\n"
        f"🍽 Foods Logged Today: {report['foods_logged_today']}\n"
        f"📦 Barcode Scans Today: {report['barcode_scans_today']}\n"
        f"📸 Food Photos Today: {report['food_photos_today']}\n\n"
        f"🧠 AI Coach Requests: {report['ai_coach_requests_today']}\n"
        f"🍱 Meal Plans Generated: {report['meal_plans_today']}\n\n"
        f"⭐ Favorites Saved: {report['favorites_saved']}\n"
        f"⚖️ Weight Entries Today: {report['weights_logged_today']}"
    )

    await update.message.reply_text(text)
