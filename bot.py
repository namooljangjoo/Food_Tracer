import os

from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from handlers.callback_handler import handle_callback
from handlers.admin_handler import admin_command
from handlers.food_handler import handle_food_message, undo
from handlers.history_handler import history
from handlers.meal_plan_handler import weekly_meal_plan
from handlers.pdf_handler import export_pdf
from handlers.photo_food_handler import handle_food_photo
from handlers.report_handler import (
    adaptive_goal,
    clear_today_request,
    nutrition_analysis,
    today,
    today_foods,
    today_progress,
    weekly_report,
)
from handlers.settings_handler import goal
from handlers.start_handler import (
    ask_calories,
    ask_language,
    ask_protein,
    cancel,
    language_command,
    start,
)
from handlers.weight_handler import (
    weight_command,
    weight_history_command,
    weight_report,
)
from states import ASK_CALORIES, ASK_LANGUAGE, ASK_PROTEIN

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def register_handlers(app):
    conversation = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("language", language_command),
        ],
        states={
            ASK_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_language)],
            ASK_CALORIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_calories)],
            ASK_PROTEIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_protein)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conversation)

    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("goal", goal))
    app.add_handler(CommandHandler("undo", undo))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("foods", today_foods))
    app.add_handler(CommandHandler("clear_today", clear_today_request))
    app.add_handler(CommandHandler("report", weekly_report))
    app.add_handler(CommandHandler("progress", today_progress))
    app.add_handler(CommandHandler("adaptive_goal", adaptive_goal))
    app.add_handler(CommandHandler("meal_plan", weekly_meal_plan))
    app.add_handler(CommandHandler("export_pdf", export_pdf))
    app.add_handler(CommandHandler("analyze", nutrition_analysis))
    app.add_handler(CommandHandler("weight", weight_command))
    app.add_handler(CommandHandler("weight_history", weight_history_command))
    app.add_handler(CommandHandler("weight_report", weight_report))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_food_photo))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_food_message))


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is missing in .env")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    register_handlers(app)

    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
