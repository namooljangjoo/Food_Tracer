import os
import uuid

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes

from adaptive_goal_service import apply_adaptive_goal
from ai_coach_service import generate_ai_coach_report
from barcode_service import get_product_by_barcode, read_barcode
from calendar_service import build_history_menu
from chart_service import generate_weight_chart
from clarification_service import apply_clarification, find_next_clarification
from coach_data_service import build_coach_data, get_coach_cooldown, mark_coach_used
from custom_food_service import estimate_custom_food, save_custom_food
from daily_summary import clear_today_foods, get_today_summary, undo_last_meal
from database import FoodLog, SessionLocal
from favorites_service import get_favorite_by_id, get_favorites, save_favorite
from food_parser import parse_food
from formatter import format_meal_response
from goals_service import get_goal
from localization_service import translate_food_name
from meal_calculator import calculate_and_save_parsed_meal
from menu_service import main_keyboard, food_keyboard, reports_keyboard, settings_keyboard, more_keyboard
from preference_service import get_preference, remember_choice
from settings_service import get_language, save_language
from shopping_service import generate_weekly_shopping_list
from streak_service import update_streak
from weight_service import save_weight
from handlers.barcode_handler import save_pending_barcode_amount
from handlers.coach_handler import ai_coach_report
from handlers.custom_food_handler import (
    handle_custom_food_confirm,
    handle_custom_food_ingredients,
    handle_custom_food_name,
)
from handlers.favorite_handler import handle_favorite_name, list_favorites, start_save_favorite
from handlers.photo_food_handler import handle_food_photo_confirm
from handlers.history_handler import history
from handlers.meal_plan_handler import weekly_meal_plan
from handlers.report_handler import today, weekly_report, nutrition_analysis, today_foods, clear_today_request, today_progress, adaptive_goal
from handlers.start_handler import language_keyboard
from handlers.weight_handler import weight_report


async def undo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"
    deleted_items = undo_last_meal(user_id)

    if not deleted_items:
        text = "Nothing found to undo." if language == "en" else "چیزی برای حذف کردن پیدا نشد."
        await update.message.reply_text(text, reply_markup=main_keyboard(language))
        return

    summary = get_today_summary(user_id)

    if language == "en":
        lines = ["↩️ Last meal removed:\n"]
        for item in deleted_items:
            lines.append(f"🍽 {item['food_name']} | {item['calories']} kcal | {item['protein']}g protein")
        lines.append("")
        lines.append("📊 New today total")
        lines.append(f"🔥 Calories: {summary['total_calories']}")
        lines.append(f"💪 Protein: {summary['total_protein']}g")
        if "calories_goal" in summary:
            lines.append("")
            lines.append(f"⌛ Remaining calories: {summary['remaining_calories']}")
            lines.append(f"⌛ Remaining protein: {summary['remaining_protein']}g")
    else:
        lines = ["↩️ آخرین وعده حذف شد:\n"]
        for item in deleted_items:
            food_name = translate_food_name(item["food_name"], language)
            lines.append(f"🍽 {food_name} | {item['calories']} کالری | {item['protein']} گرم پروتئین")
        lines.append("")
        lines.append("📊 مجموع جدید امروز")
        lines.append(f"🔥 کالری: {summary['total_calories']}")
        lines.append(f"💪 پروتئین: {summary['total_protein']} گرم")
        if "calories_goal" in summary:
            lines.append("")
            lines.append(f"⌛ باقی‌مانده کالری: {summary['remaining_calories']}")
            lines.append(f"⌛ باقی‌مانده پروتئین: {summary['remaining_protein']} گرم")

    await update.message.reply_text("\n".join(lines), reply_markup=main_keyboard(language))
async def handle_food_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    print(f"BUTTON CLICKED: {text}", flush=True)
    language = get_language(user_id) or "fa"

    if text in ["⬅️ بازگشت", "⬅️ Back"]:
        cancel_active_requests(context)
        await update.message.reply_text(
            "🏠 منوی اصلی" if language == "fa" else "🏠 Main menu",
            reply_markup=main_keyboard(language),
        )
        return

    if context.user_data.get("awaiting_favorite_name"):
        await handle_favorite_name(update, context)
        return

    if context.user_data.get("awaiting_custom_food_name"):
        await handle_custom_food_name(update, context)
        return

    if context.user_data.get("awaiting_custom_food_ingredients"):
        await handle_custom_food_ingredients(update, context)
        return

    if context.user_data.get("awaiting_custom_food_confirm"):
        await handle_custom_food_confirm(update, context)
        return


    if text in ["🍽 غذا", "🍽 Food"]:
        await update.message.reply_text(
            "🍽 منوی غذا" if language == "fa" else "🍽 Food menu",
            reply_markup=food_keyboard(language),
        )
        return

    if text in ["📊 گزارش‌ها", "📊 Reports"]:
        await update.message.reply_text(
            "📊 گزارش‌ها" if language == "fa" else "📊 Reports",
            reply_markup=reports_keyboard(language),
        )
        return

    if text in ["⚙️ تنظیمات", "⚙️ Settings"]:
        await update.message.reply_text(
            "⚙️ تنظیمات" if language == "fa" else "⚙️ Settings",
            reply_markup=settings_keyboard(language),
        )
        return

    if text in ["ℹ️ بیشتر", "ℹ️ More"]:
        await update.message.reply_text(
            "ℹ️ بیشتر" if language == "fa" else "ℹ️ More",
            reply_markup=more_keyboard(language),
        )
        return

    if text in ["📅 امروز", "📅 Today", "📊 امروز", "📊 Today"]:
        await today(update, context)
        return

    if text in ["📈 گزارش هفتگی", "📈 Weekly Report"]:
        await weekly_report(update, context)
        return

    if text in ["🛒 لیست خرید", "🛒 Shopping List"]:
        await shopping_list(update, context)
        return

    if text in ["🍱 برنامه غذایی", "🍱 Meal Plan"]:
        await weekly_meal_plan(update, context)
        return

    if text in ["🎯 پیشرفت امروز", "🎯 Today Progress"]:
        await today_progress(update, context)
        return

    if text in ["🎯 پیشنهاد هدف", "🎯 Adaptive Goal"]:
        await adaptive_goal(update, context)
        return

    if text in ["🧠 تحلیل تغذیه", "🧠 Nutrition Analysis"]:
        await nutrition_analysis(update, context)
        return

    if text in ["🧠 مربی من", "🧠 My Coach"]:
        await ai_coach_report(update, context)
        return

    if text in ["⚖️ روند وزن", "⚖️ Weight Trend", "⚖️ گزارش وزن", "⚖️ Weight Report", "⚖️ Weight report"]:
        await weight_report(update, context)
        return

    if text in ["📜 تاریخچه", "📜 History", "📅 تاریخچه", "📅 History"]:
        await update.message.reply_text(
            "📅 بازه تاریخچه را انتخاب کن:" if language == "fa"
            else "📅 Choose history range:",
            reply_markup=build_history_menu(language),
        )
        return

    if text in ["ℹ️ درباره", "ℹ️ About"]:
        await update.message.reply_text(
            "FoodTracer v1.0",
            reply_markup=more_keyboard(language),
        )
        return

    if text in ["🎯 اهداف", "🎯 Goals"]:
        await update.message.reply_text(
            "برای تغییر هدف اینطوری بنویس:\n/goal 1700 200"
            if language == "fa"
            else "Use this format:\n/goal 1700 200",
            reply_markup=settings_keyboard(language),
        )
        return

    if text in ["🌍 زبان", "🌍 Language", "🌐 تغییر زبان", "🌐 Change language"]:
        context.user_data["changing_language_only"] = True
        await update.message.reply_text(
            "Please choose your language:\n\nلطفاً زبان خود را انتخاب کنید:",
            reply_markup=language_keyboard(),
        )
        return

    if text in ["⚖️ ثبت وزن", "⚖️ Log Weight", "⚖️ Log weight"]:
        context.user_data["awaiting_weight"] = True
        await update.message.reply_text(
            "Enter your current weight:\n\nExample:\n82.5"
            if language == "en"
            else "وزن فعلی‌ات را وارد کن:\n\nمثال:\n82.5"
        )
        return

    if text in ["➕ ثبت غذا", "➕ Log Food"]:
        await update.message.reply_text(
            "غذایت را بنویس."
            if language == "fa"
            else "Send your meal.",
            reply_markup=food_keyboard(language),
        )
        return

    if text in ["➕ غذای سفارشی", "➕ Custom Food"]:
        context.user_data["awaiting_custom_food_name"] = True

        await update.message.reply_text(
            "اسم غذا را بنویس:\n\nمثال:\nنان پروتئینی خانگی"
            if language == "fa"
            else
            "Send the food name:\n\nExample:\nHomemade protein bread",
            reply_markup=food_keyboard(language)
        )
        return

    if text in ["📸 عکس غذا", "📸 Food Photo"]:
        context.user_data["awaiting_food_photo"] = True

        await update.message.reply_text(
            "لطفاً عکس غذا را بفرست."
            if language == "fa"
            else "Please send the food photo.",
            reply_markup=food_keyboard(language),
        )
        return

    if text in ["⭐ ذخیره محبوب", "⭐ Save Favorite"]:
        await start_save_favorite(update, context)
        return

    if text in ["⭐ غذاهای محبوب", "⭐ Favorites"]:
        await list_favorites(update, context)
        return

    if text in ["📦 اسکن بارکد", "📦 Scan barcode", "📦 Scan Barcode"]:
        await update.message.reply_text(
            "Please send a clear photo of the barcode."
            if language == "en"
            else "لطفاً یک عکس واضح از بارکد محصول بفرست.",
            reply_markup=food_keyboard(language),
        )
        return

    if text in ["↩️ حذف آخرین غذا", "↩️ Undo Last Meal", "↩️ حذف آخرین وعده", "↩️ Undo last meal"]:
        await undo(update, context)
        return

    if text in ["📋 غذاهای امروز", "📋 Today foods"]:
        await today_foods(update, context)
        return

    if text in ["🧹 پاک کردن امروز", "🧹 Clear today", "🧹 Clear Today"]:
        await clear_today_request(update, context)
        return

    if text in ["فارسی", "English"]:
        new_language = "fa" if text == "فارسی" else "en"
        save_language(user_id, new_language)
        await update.message.reply_text(
            "English selected ✅" if new_language == "en" else "زبان فارسی انتخاب شد ✅",
            reply_markup=main_keyboard(new_language),
        )
        return

    if context.user_data.get("awaiting_barcode_amount"):
        await save_pending_barcode_amount(update, context)
        return

    if context.user_data.get("awaiting_clear_today_confirm"):
        if text in ["بله", "YES", "Yes", "yes"]:
            deleted_count = clear_today_foods(user_id)
            context.user_data["awaiting_clear_today_confirm"] = False
            msg = (
                f"✅ Cleared {deleted_count} foods from today."
                if language == "en"
                else f"✅ {deleted_count} مورد از غذاهای امروز پاک شد."
            )
            await update.message.reply_text(msg, reply_markup=main_keyboard(language))
            return

        context.user_data["awaiting_clear_today_confirm"] = False
        await update.message.reply_text(
            "Clear today cancelled." if language == "en" else "پاک کردن امروز لغو شد.",
            reply_markup=main_keyboard(language),
        )
        return

    if context.user_data.get("awaiting_weight"):
        try:
            weight = float(text.replace(",", "."))
            if weight < 20 or weight > 500:
                raise ValueError()

            save_weight(user_id, weight)
            context.user_data["awaiting_weight"] = False

            await update.message.reply_text(
                f"✅ Weight saved: {weight} kg"
                if language == "en"
                else f"✅ وزن ثبت شد: {weight} kg",
                reply_markup=main_keyboard(language),
            )
            return

        except Exception:
            await update.message.reply_text(
                "Enter only a number.\nExample: 82.5"
                if language == "en"
                else "فقط عدد وارد کن.\nمثال: 82.5"
            )
            return

    if context.user_data.get("awaiting_goal_suggestion_confirm"):
        if text in ["بله", "YES", "Yes", "yes"]:
            suggestion = context.user_data.get("pending_goal_suggestion")

            if suggestion:
                apply_adaptive_goal(user_id, suggestion)

            context.user_data["awaiting_goal_suggestion_confirm"] = False
            context.user_data.pop("pending_goal_suggestion", None)

            await update.message.reply_text(
                "✅ هدف جدید ذخیره شد."
                if language == "fa"
                else "✅ New goal saved.",
                reply_markup=reports_keyboard(language),
            )
            return

        if text in ["نه", "NO", "No", "no"]:
            context.user_data["awaiting_goal_suggestion_confirm"] = False
            context.user_data.pop("pending_goal_suggestion", None)

            await update.message.reply_text(
                "لغو شد."
                if language == "fa"
                else "Cancelled.",
                reply_markup=reports_keyboard(language),
            )
            return

        await update.message.reply_text(
            "لطفاً بله یا نه بنویس."
            if language == "fa"
            else "Please answer YES or NO."
        )
        return

    if context.user_data.get("awaiting_clarification"):
        parsed_foods = context.user_data.get("pending_parsed_foods")
        item_index = context.user_data.get("pending_clarification_index")
        clarification = context.user_data.get("pending_clarification")

        updated = apply_clarification(
            parsed_foods,
            item_index,
            text,
            clarification,
            language,
        )

        if not updated:
            await update.message.reply_text(
                "لطفاً یکی از گزینه‌ها را انتخاب کن."
                if language == "fa"
                else "Please choose one of the options.",
                reply_markup=clarification["keyboard"],
            )
            return

        selected_item = updated[item_index]

        remember_choice(
            user_id,
            clarification["original_food"],
            selected_item["food"],
            selected_item["unit"],
        )

        next_index, next_clarification = find_next_clarification(
            updated,
            item_index + 1,
            language,
        )

        if next_clarification:
            context.user_data["pending_parsed_foods"] = updated
            context.user_data["pending_clarification_index"] = next_index
            context.user_data["pending_clarification"] = next_clarification

            await update.message.reply_text(
                next_clarification["question"],
                reply_markup=next_clarification["keyboard"],
            )
            return

        context.user_data["awaiting_clarification"] = False

        meal_result = calculate_and_save_parsed_meal(updated, user_id)
        original_text = context.user_data.get("pending_original_food_text")

        context.user_data.pop("pending_parsed_foods", None)
        context.user_data.pop("pending_clarification_index", None)
        context.user_data.pop("pending_clarification", None)
        context.user_data.pop("pending_original_food_text", None)

        if not meal_result["items"]:
            await update.message.reply_text(
                "نتونستم این غذا رو محاسبه کنم. لطفاً واضح‌تر بنویس."
                if language == "fa"
                else "I could not calculate this food. Please write it more clearly.",
                reply_markup=main_keyboard(language),
            )
            return

        if original_text:
            context.user_data["last_food_text"] = original_text

        today_summary = get_today_summary(user_id)
        streak = update_streak(user_id)
        message = format_meal_response(meal_result, today_summary, language)

        if language == "en":
            message += f"\n\n🔥 Current Streak: {streak['current']} days"
        else:
            message += f"\n\n🔥 استریک فعلی: {streak['current']} روز"

        await update.message.reply_text(
            message,
            reply_markup=main_keyboard(language),
        )
        return

    goal_data = get_goal(user_id)

    if not goal_data:
        await update.message.reply_text(
            "Please use /start first." if language == "en" else "اول /start را بزن."
        )
        return

    if context.user_data.get("awaiting_food_photo_confirm"):
        await handle_food_photo_confirm(update, context)
        return

    if text.startswith("⭐ "):
        try:
            favorite_id = int(text.replace("⭐ ", ""))

            favorite = get_favorite_by_id(favorite_id)

            if not favorite or favorite.user_id != user_id:
                raise ValueError()

            text = favorite.food_text

        except Exception:
            await update.message.reply_text(
                "محبوب پیدا نشد."
                if language == "fa"
                else
                "Favorite not found."
            )
            return

    try:
        parsed_foods = parse_food(text)

        for item in parsed_foods:
            preference = get_preference(
                user_id,
                item["food"],
            )

            if preference:
                item["food"] = preference["food"]
                item["unit"] = preference["unit"]
                item["_preference_applied"] = True

        clarification_index, clarification = find_next_clarification(
            parsed_foods,
            0,
            language,
        )

        if clarification:
            context.user_data["awaiting_clarification"] = True
            context.user_data["pending_parsed_foods"] = parsed_foods
            context.user_data["pending_clarification_index"] = clarification_index
            context.user_data["pending_clarification"] = clarification
            context.user_data["pending_original_food_text"] = text

            await update.message.reply_text(
                clarification["question"],
                reply_markup=clarification["keyboard"],
            )
            return

        meal_result = calculate_and_save_parsed_meal(parsed_foods, user_id)

        if not meal_result["items"]:
            await update.message.reply_text(
                "I could not calculate this food. Please write it more clearly."
                if language == "en"
                else "نتونستم این غذا رو محاسبه کنم. لطفاً واضح‌تر بنویس.",
                reply_markup=main_keyboard(language),
            )
            return

        context.user_data["last_food_text"] = text

        today_summary = get_today_summary(user_id)
        streak = update_streak(user_id)
        message = format_meal_response(meal_result, today_summary, language)

        if language == "en":
            message += f"\n\n🔥 Current Streak: {streak['current']} days"
        else:
            message += f"\n\n🔥 استریک فعلی: {streak['current']} روز"

        await update.message.reply_text(
            message,
            reply_markup=main_keyboard(language),
        )

    except Exception as e:
        await update.message.reply_text(
            "Something went wrong. Please write the food more clearly."
            if language == "en"
            else "مشکلی پیش اومد. لطفاً غذا رو واضح‌تر بنویس."
        )
        print("ERROR:", e, flush=True)
def cancel_active_requests(context):
    keys_to_cancel = [
        "awaiting_weight",
        "awaiting_barcode_amount",
        "pending_barcode_product",
        "awaiting_clear_today_confirm",
        "awaiting_custom_food_name",
        "awaiting_custom_food_ingredients",
        "awaiting_custom_food_confirm",
        "custom_food_name",
        "pending_custom_food",
        "awaiting_favorite_name",
        "awaiting_food_photo",
        "awaiting_food_photo_confirm",
        "pending_food_photo_result",
        "awaiting_goal_suggestion_confirm",
        "pending_goal_suggestion",
        "awaiting_clarification",
        "pending_parsed_foods",
        "pending_clarification_index",
        "pending_clarification",
        "pending_original_food_text",
        "history_start",
        "changing_language_only",
        "calories_goal",
    ]

    for key in keys_to_cancel:
        if key in context.user_data:
            context.user_data.pop(key, None)
