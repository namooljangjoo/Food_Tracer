import os

from telegram import Update
from telegram.ext import ContextTypes

from menu_service import reports_keyboard
from pdf_service import generate_weekly_pdf
from settings_service import get_language


async def export_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"
    pdf_path = None

    await update.message.reply_text(
        "📄 در حال ساخت PDF..."
        if language == "fa"
        else "📄 Generating PDF...",
        reply_markup=reports_keyboard(language),
    )

    try:
        pdf_path = generate_weekly_pdf(user_id)

        with open(pdf_path, "rb") as file:
            await update.message.reply_document(
                document=file,
                filename="FoodTracer_Report.pdf",
                reply_markup=reports_keyboard(language),
            )

    except Exception as error:
        print("PDF EXPORT ERROR:", repr(error), flush=True)

        await update.message.reply_text(
            "نتونستم فایل PDF بسازم."
            if language == "fa"
            else "I couldn't generate the PDF.",
            reply_markup=reports_keyboard(language),
        )

    finally:
        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)
