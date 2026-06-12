import os
import uuid

from telegram import Update
from telegram.ext import ContextTypes

from analytics_service import track_event
from daily_summary import get_today_summary
from database import FoodLog, SessionLocal
from streak_service import update_streak
from food_photo_service import analyze_food_photo
from menu_service import food_keyboard
from settings_service import get_language
from handlers.barcode_handler import handle_barcode_photo


async def handle_food_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"

    if not context.user_data.get("awaiting_food_photo"):
        await handle_barcode_photo(update, context)
        return

    photo_path = None

    try:
        photo = update.message.photo[-1]
        telegram_file = await photo.get_file()

        photo_path = f"/tmp/food_photo_{user_id}_{uuid.uuid4()}.jpg"

        await telegram_file.download_to_drive(photo_path)

        await update.message.reply_text(
            "در حال تحلیل عکس غذا..."
            if language == "fa"
            else "Analyzing food photo..."
        )

        result = analyze_food_photo(photo_path)

        context.user_data["pending_food_photo_result"] = result
        context.user_data["awaiting_food_photo"] = False
        context.user_data["awaiting_food_photo_confirm"] = True

        lines = []

        if language == "fa":
            lines.append("📸 نتیجه تخمینی عکس غذا:\n")
            for item in result["items"]:
                lines.append(
                    f"🍽 {item['food']} | "
                    f"{item['grams']} گرم | "
                    f"{item['calories']} کالری | "
                    f"{item['protein']} گرم پروتئین"
                )

            lines.append("")
            lines.append(f"🔥 مجموع کالری: {result['total_calories']}")
            lines.append(f"💪 مجموع پروتئین: {result['total_protein']} گرم")
            lines.append("")
            lines.append("ثبت شود؟ بله / نه")
        else:
            lines.append("📸 Estimated food photo result:\n")
            for item in result["items"]:
                lines.append(
                    f"🍽 {item['food']} | "
                    f"{item['grams']}g | "
                    f"{item['calories']} kcal | "
                    f"{item['protein']}g protein"
                )

            lines.append("")
            lines.append(f"🔥 Total calories: {result['total_calories']}")
            lines.append(f"💪 Total protein: {result['total_protein']}g")
            lines.append("")
            lines.append("Save it? YES / NO")

        await update.message.reply_text(
            "\n".join(lines),
            reply_markup=food_keyboard(language),
        )

    except Exception as e:
        print("FOOD PHOTO ERROR:", repr(e), flush=True)

        await update.message.reply_text(
            "نتونستم عکس غذا را تحلیل کنم. لطفاً عکس واضح‌تری بفرست."
            if language == "fa"
            else "I couldn't analyze the food photo. Please send a clearer photo.",
            reply_markup=food_keyboard(language),
        )

        context.user_data["awaiting_food_photo"] = False

    finally:
        if photo_path and os.path.exists(photo_path):
            os.remove(photo_path)

async def handle_food_photo_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    language = get_language(user_id) or "fa"
    if text in ["بله", "YES", "Yes", "yes"]:
        result = context.user_data.get("pending_food_photo_result")

        if not result:
            context.user_data["awaiting_food_photo_confirm"] = False
            await update.message.reply_text(
                "چیزی برای ثبت پیدا نشد."
                if language == "fa"
                else "Nothing found to save.",
                reply_markup=food_keyboard(language),
            )
            return

        db = SessionLocal()
        meal_id = str(uuid.uuid4())

        for item in result["items"]:
            db.add(
                FoodLog(
                    user_id=user_id,
                    meal_id=meal_id,
                    food_name=item["food"],
                    calories=float(item["calories"]),
                    protein=float(item["protein"]),
                )
            )

        db.commit()

        if language == "fa":
            food_text = ", ".join(
                [f"{item['grams']} گرم {item['food']}" for item in result["items"]]
            )
        else:
            food_text = ", ".join(
                [f"{item['grams']}g {item['food']}" for item in result["items"]]
            )

        context.user_data["last_food_text"] = food_text

        db.close()
        track_event(user_id, "food_logged")
        track_event(user_id, "food_photo")

        context.user_data["awaiting_food_photo_confirm"] = False
        context.user_data.pop("pending_food_photo_result", None)

        today_summary = get_today_summary(user_id)
        streak = update_streak(user_id)

        msg = (
            (
                f"✅ عکس غذا ثبت شد.\n\n"
                f"🔥 مجموع امروز: {today_summary['total_calories']} کالری\n"
                f"💪 پروتئین امروز: {today_summary['total_protein']} گرم"
                f"\n\n🔥 استریک فعلی: {streak['current']} روز"
            )
            if language == "fa"
            else
            (
                f"✅ Food photo logged.\n\n"
                f"🔥 Today calories: {today_summary['total_calories']}\n"
                f"💪 Today protein: {today_summary['total_protein']}g"
                f"\n\n🔥 Current Streak: {streak['current']} days"
            )
        )

        await update.message.reply_text(
            msg,
            reply_markup=food_keyboard(language),
        )
        return

    if text in ["نه", "NO", "No", "no"]:
        context.user_data["awaiting_food_photo_confirm"] = False
        context.user_data.pop("pending_food_photo_result", None)

        await update.message.reply_text(
            "لغو شد." if language == "fa" else "Cancelled.",
            reply_markup=food_keyboard(language),
        )
        return

    await update.message.reply_text(
        "لطفاً بله یا نه بنویس."
        if language == "fa"
        else "Please answer YES or NO."
    )
    return
