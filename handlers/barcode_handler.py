import os
import uuid

from telegram import Update
from telegram.ext import ContextTypes

from analytics_service import track_event
from barcode_service import read_barcode, get_product_by_barcode
from daily_summary import get_today_summary
from database import FoodLog, SessionLocal
from menu_service import main_keyboard
from settings_service import get_language
from streak_service import update_streak


async def handle_barcode_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"

    photo_path = None

    try:
        photo = update.message.photo[-1]
        telegram_file = await photo.get_file()

        photo_path = f"/tmp/barcode_{user_id}_{uuid.uuid4()}.jpg"

        await telegram_file.download_to_drive(photo_path)

        barcode = read_barcode(photo_path)

        if not barcode:
            msg = (
                "I couldn't detect a barcode. Please send a clearer photo."
                if language == "en"
                else "نتونستم بارکد رو تشخیص بدم. لطفاً عکس واضح‌تری بفرست."
            )
            await update.message.reply_text(msg, reply_markup=main_keyboard(language))
            return

        product = get_product_by_barcode(barcode)

        if not product:
            msg = (
                f"Barcode detected: {barcode}\n\nProduct not found."
                if language == "en"
                else f"بارکد تشخیص داده شد: {barcode}\n\nمحصول پیدا نشد."
            )
            await update.message.reply_text(msg, reply_markup=main_keyboard(language))
            return

        context.user_data["pending_barcode_product"] = product
        context.user_data["awaiting_barcode_amount"] = True

        if language == "en":
            text = (
                "📦 Product found:\n\n"
                f"Name: {product['name']}\n"
                f"Brand: {product['brand']}\n"
                f"Barcode: {product['barcode']}\n\n"
                "Per 100g:\n"
                f"🔥 Calories: {product['calories_per_100g']}\n"
                f"💪 Protein: {product['protein_per_100g']}g\n\n"
                "How many grams did you eat?\n"
                "Example: 50"
            )
        else:
            text = (
                "📦 محصول پیدا شد:\n\n"
                f"نام: {product['name']}\n"
                f"برند: {product['brand']}\n"
                f"بارکد: {product['barcode']}\n\n"
                "در هر ۱۰۰ گرم:\n"
                f"🔥 کالری: {product['calories_per_100g']}\n"
                f"💪 پروتئین: {product['protein_per_100g']} گرم\n\n"
                "چند گرم مصرف کردی؟\n"
                "مثال: 50"
            )

        await update.message.reply_text(text, reply_markup=main_keyboard(language))

    except Exception as e:
        print("BARCODE ERROR:", repr(e))

        msg = (
            "Something went wrong while scanning the barcode."
            if language == "en"
            else "مشکلی موقع اسکن بارکد پیش اومد."
        )

        await update.message.reply_text(msg, reply_markup=main_keyboard(language))

    finally:
        if photo_path and os.path.exists(photo_path):
            os.remove(photo_path)
async def save_pending_barcode_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"
    text = update.message.text.strip()

    try:
        grams = float(text.replace(",", "."))

        if grams <= 0 or grams > 5000:
            raise ValueError()

        product = context.user_data.get("pending_barcode_product")

        if not product:
            context.user_data["awaiting_barcode_amount"] = False
            msg = (
                "No pending barcode product found. Please scan again."
                if language == "en"
                else "محصولی برای ثبت پیدا نشد. لطفاً دوباره اسکن کن."
            )
            await update.message.reply_text(msg, reply_markup=main_keyboard(language))
            return

        calories = round(product["calories_per_100g"] * grams / 100, 1)
        protein = round(product["protein_per_100g"] * grams / 100, 1)

        db = SessionLocal()

        food_log = FoodLog(
            user_id=user_id,
            meal_id=str(uuid.uuid4()),
            food_name=product["name"],
            calories=calories,
            protein=protein,
        )

        db.add(food_log)
        db.commit()
        db.close()
        track_event(user_id, "food_logged")
        track_event(user_id, "barcode_scan")

        context.user_data["awaiting_barcode_amount"] = False
        context.user_data["pending_barcode_product"] = None

        today_summary = get_today_summary(user_id)
        streak = update_streak(user_id)

        if language == "en":
            msg = (
                "✅ Product logged:\n\n"
                f"📦 {product['name']}\n"
                f"⚖️ Amount: {grams}g\n"
                f"🔥 Calories: {calories}\n"
                f"💪 Protein: {protein}g\n\n"
                "📊 Today total:\n"
                f"🔥 Calories: {today_summary['total_calories']}\n"
                f"💪 Protein: {today_summary['total_protein']}g"
            )
        else:
            msg = (
                "✅ محصول ثبت شد:\n\n"
                f"📦 {product['name']}\n"
                f"⚖️ مقدار: {grams} گرم\n"
                f"🔥 کالری: {calories}\n"
                f"💪 پروتئین: {protein} گرم\n\n"
                "📊 مجموع امروز:\n"
                f"🔥 کالری: {today_summary['total_calories']}\n"
                f"💪 پروتئین: {today_summary['total_protein']} گرم"
            )

        if language == "en":
            msg += f"\n\n🔥 Current Streak: {streak['current']} days"
        else:
            msg += f"\n\n🔥 استریک فعلی: {streak['current']} روز"

        await update.message.reply_text(msg, reply_markup=main_keyboard(language))

    except Exception:
        msg = (
            "Please enter only the amount in grams.\nExample: 50"
            if language == "en"
            else "فقط مقدار را به گرم وارد کن.\nمثال: 50"
        )

        await update.message.reply_text(msg)
