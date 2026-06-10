import os
import uuid

from database import FoodLog, SessionLocal
from barcode_service import read_barcode, get_product_by_barcode
from datetime import date, timedelta
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)
from meal_calculator import calculate_and_save_meal
from daily_summary import (
    get_today_summary,
    undo_last_meal,
    get_today_foods,
    clear_today_foods,
)
from formatter import format_meal_response
from goals_service import save_goal, get_goal
from settings_service import save_language, get_language
from localization_service import translate_food_name
from history_service import get_history_range
from history_formatter import format_history
from calendar_service import build_history_menu, build_calendar
from report_service import get_weekly_report
from chart_service import create_weekly_chart, create_weight_chart
from weight_service import save_weight, get_weight_history
from analysis_service import analyze_nutrition
from analysis_formatter import format_analysis
from barcode_service import read_barcode
from menu_service import (
    main_keyboard,
    food_keyboard,
    reports_keyboard,
    settings_keyboard,
    more_keyboard,
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

ASK_LANGUAGE, ASK_CALORIES, ASK_PROTEIN = range(3)



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

    text = (
        "Hi 👋\n\nEverything is ready. Just send what you ate."
        if language == "en"
        else "سلام 👋\n\nهمه چیز آماده است. هر غذایی خوردی فقط بنویس."
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


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"
    summary = get_today_summary(user_id)

    if language == "en":
        text = (
            "📊 Today\n"
            f"🔥 Calories: {summary['total_calories']}\n"
            f"💪 Protein: {summary['total_protein']}g"
        )

        if "calories_goal" in summary:
            text += (
                "\n\n"
                f"🎯 Calorie goal: {summary['calories_goal']}\n"
                f"🎯 Protein goal: {summary['protein_goal']}g\n\n"
                f"⌛ Remaining calories: {summary['remaining_calories']}\n"
                f"⌛ Remaining protein: {summary['remaining_protein']}g"
            )
    else:
        text = (
            "📊 مجموع امروز\n"
            f"🔥 کالری: {summary['total_calories']}\n"
            f"💪 پروتئین: {summary['total_protein']} گرم"
        )

        if "calories_goal" in summary:
            text += (
                "\n\n"
                f"🎯 هدف کالری: {summary['calories_goal']}\n"
                f"🎯 هدف پروتئین: {summary['protein_goal']} گرم\n\n"
                f"⌛ باقی‌مانده کالری: {summary['remaining_calories']}\n"
                f"⌛ باقی‌مانده پروتئین: {summary['remaining_protein']} گرم"
            )

    await update.message.reply_text(text, reply_markup=main_keyboard(language))


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


async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"

    try:
        if len(context.args) == 2:
            from history_service import parse_date
            start_date = parse_date(context.args[0])
            end_date = parse_date(context.args[1])

            if start_date > end_date:
                text = "Start date cannot be after end date." if language == "en" else "تاریخ شروع نباید بعد از تاریخ پایان باشد."
                await update.message.reply_text(text)
                return
            history_data = get_history_range(user_id, start_date, end_date)
        else:
            history_data = get_history_range(user_id)

        text = format_history(history_data, language)
        await update.message.reply_text(text, reply_markup=main_keyboard(language))

    except Exception:
        text = (
            "Correct format:\n/history 2026-06-01 2026-06-08"
            if language == "en"
            else "فرمت درست:\n/history 2026-06-01 2026-06-08"
        )
        await update.message.reply_text(text)


async def weekly_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"

    report = get_weekly_report(user_id)
    chart_path = create_weekly_chart(report, user_id)

    if language == "en":
        caption = (
            "📈 Weekly Report\n\n"
            f"🔥 Average calories: {report['average_calories']}\n"
            f"💪 Average protein: {report['average_protein']}g\n"
            f"📌 Logged days: {report['logged_days_count']} / 7"
        )
        if report["latest_weight"]:
            caption += f"\n⚖️ Latest weight: {report['latest_weight']} kg"
    else:
        caption = (
            "📈 گزارش هفتگی\n\n"
            f"🔥 میانگین کالری: {report['average_calories']}\n"
            f"💪 میانگین پروتئین: {report['average_protein']} گرم\n"
            f"📌 روزهای ثبت‌شده: {report['logged_days_count']} / 7"
        )
        if report["latest_weight"]:
            caption += f"\n⚖️ آخرین وزن: {report['latest_weight']} kg"

    with open(chart_path, "rb") as photo:
        await update.message.reply_photo(photo=photo, caption=caption, reply_markup=main_keyboard(language))

    try:
        os.remove(chart_path)
    except Exception:
        pass


async def nutrition_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"

    analysis = analyze_nutrition(user_id)
    text = format_analysis(analysis, language)

    await update.message.reply_text(text, reply_markup=main_keyboard(language))


async def today_foods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"
    foods = get_today_foods(user_id)

    if not foods:
        text = "No food has been logged today." if language == "en" else "امروز هنوز غذایی ثبت نشده."
        await update.message.reply_text(text, reply_markup=main_keyboard(language))
        return

    if language == "en":
        lines = ["📋 Today foods\n"]
        for item in foods:
            lines.append(f"🍽 {item['food_name']} | {item['calories']} kcal | {item['protein']}g protein")
    else:
        lines = ["📋 غذاهای امروز\n"]
        for item in foods:
            food_name = translate_food_name(item["food_name"], language)
            lines.append(f"🍽 {food_name} | {item['calories']} کالری | {item['protein']} گرم پروتئین")

    summary = get_today_summary(user_id)

    if language == "en":
        lines.append("")
        lines.append(f"🔥 Total calories: {summary['total_calories']}")
        lines.append(f"💪 Total protein: {summary['total_protein']}g")
    else:
        lines.append("")
        lines.append(f"🔥 مجموع کالری: {summary['total_calories']}")
        lines.append(f"💪 مجموع پروتئین: {summary['total_protein']} گرم")

    await update.message.reply_text("\n".join(lines), reply_markup=main_keyboard(language))


async def clear_today_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = get_language(update.effective_user.id) or "fa"
    context.user_data["awaiting_clear_today_confirm"] = True

    text = (
        "Are you sure you want to clear all foods logged today?\n\nType YES to confirm."
        if language == "en"
        else "مطمئنی می‌خوای همه غذاهای امروز پاک بشن؟\n\nبرای تأیید بنویس: بله"
    )

    await update.message.reply_text(text, reply_markup=main_keyboard(language))


async def weight_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"

    try:
        weight = float(context.args[0].replace(",", "."))
        if weight < 20 or weight > 500:
            raise ValueError()

        save_weight(user_id, weight)
        text = f"✅ Weight saved: {weight} kg" if language == "en" else f"✅ وزن ثبت شد: {weight} kg"
        await update.message.reply_text(text, reply_markup=main_keyboard(language))

    except Exception:
        text = "Correct format:\n/weight 82.5" if language == "en" else "فرمت درست:\n/weight 82.5"
        await update.message.reply_text(text)


async def weight_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"
    history_data = get_weight_history(user_id)

    if not history_data:
        text = "No weight has been logged yet." if language == "en" else "هنوز وزنی ثبت نشده."
        await update.message.reply_text(text, reply_markup=main_keyboard(language))
        return

    lines = ["⚖️ Weight history\n"] if language == "en" else ["⚖️ تاریخچه وزن\n"]
    for item in history_data:
        lines.append(f"📆 {item['date']} | {item['weight']} kg")

    await update.message.reply_text("\n".join(lines), reply_markup=main_keyboard(language))


async def weight_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"
    history_data = get_weight_history(user_id, days=30)

    if len(history_data) < 2:
        text = (
            "Log weight at least 2 different days to create a chart."
            if language == "en"
            else "برای ساخت نمودار وزن، حداقل در ۲ روز مختلف وزن ثبت کن."
        )
        await update.message.reply_text(text, reply_markup=main_keyboard(language))
        return

    chart_path = create_weight_chart(history_data, user_id)

    caption = "⚖️ Weight Report" if language == "en" else "⚖️ گزارش وزن"

    with open(chart_path, "rb") as photo:
        await update.message.reply_photo(photo=photo, caption=caption, reply_markup=main_keyboard(language))

    try:
        os.remove(chart_path)
    except Exception:
        pass


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = get_language(user_id) or "fa"
    data = query.data
    today_date = date.today()

    if data == "ignore":
        return

    if data == "hist:cancel":
        await query.edit_message_text("Cancelled." if language == "en" else "لغو شد.")
        return

    if data == "hist:today":
        history_data = get_history_range(user_id, today_date, today_date)

    elif data == "hist:yesterday":
        yesterday = today_date - timedelta(days=1)
        history_data = get_history_range(user_id, yesterday, yesterday)

    elif data == "hist:last7":
        start = today_date - timedelta(days=6)
        history_data = get_history_range(user_id, start, today_date)

    elif data == "hist:last30":
        start = today_date - timedelta(days=29)
        history_data = get_history_range(user_id, start, today_date)

    elif data == "hist:custom":
        text = "📅 Choose start date:" if language == "en" else "📅 تاریخ شروع را انتخاب کن:"
        await query.edit_message_text(text, reply_markup=build_calendar(purpose="start"))
        return

    elif data.startswith("cal:"):
        _, purpose, year, month, action = data.split(":")
        year = int(year)
        month = int(month)

        if action == "prev":
            month -= 1
            if month == 0:
                month = 12
                year -= 1

        elif action == "next":
            month += 1
            if month == 13:
                month = 1
                year += 1

        await query.edit_message_reply_markup(reply_markup=build_calendar(year, month, purpose))
        return

    elif data.startswith("date:"):
        _, purpose, selected_date = data.split(":")
        selected = date.fromisoformat(selected_date)

        if purpose == "start":
            context.user_data["history_start"] = selected
            text = "📅 Choose end date:" if language == "en" else "📅 تاریخ پایان را انتخاب کن:"
            await query.edit_message_text(text, reply_markup=build_calendar(purpose="end"))
            return

        if purpose == "end":
            start = context.user_data.get("history_start")
            end = selected

            if not start:
                text = "Please try again." if language == "en" else "لطفاً دوباره تلاش کن."
                await query.edit_message_text(text)
                return

            if start > end:
                text = "Start date cannot be after end date." if language == "en" else "تاریخ شروع نباید بعد از تاریخ پایان باشد."
                await query.edit_message_text(text)
                return

            history_data = get_history_range(user_id, start, end)
    else:
        return

    text = format_history(history_data, language)
    await query.edit_message_text(text)

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

        context.user_data["awaiting_barcode_amount"] = False
        context.user_data["pending_barcode_product"] = None

        today_summary = get_today_summary(user_id)

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

        await update.message.reply_text(msg, reply_markup=main_keyboard(language))

    except Exception:
        msg = (
            "Please enter only the amount in grams.\nExample: 50"
            if language == "en"
            else "فقط مقدار را به گرم وارد کن.\nمثال: 50"
        )

        await update.message.reply_text(msg)

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

    if text in ["🧠 تحلیل تغذیه", "🧠 Nutrition Analysis"]:
        await nutrition_analysis(update, context)
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

    goal_data = get_goal(user_id)

    if not goal_data:
        await update.message.reply_text(
            "Please use /start first." if language == "en" else "اول /start را بزن."
        )
        return

    try:
        meal_result = calculate_and_save_meal(text, user_id)

        if not meal_result["items"]:
            await update.message.reply_text(
                "I could not calculate this food. Please write it more clearly."
                if language == "en"
                else "نتونستم این غذا رو محاسبه کنم. لطفاً واضح‌تر بنویس.",
                reply_markup=main_keyboard(language),
            )
            return

        today_summary = get_today_summary(user_id)
        message = format_meal_response(meal_result, today_summary, language)

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


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is missing in .env")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

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
    app.add_handler(CommandHandler("analyze", nutrition_analysis))
    app.add_handler(CommandHandler("weight", weight_command))
    app.add_handler(CommandHandler("weight_history", weight_history_command))
    app.add_handler(CommandHandler("weight_report", weight_report))
    app.add_handler(MessageHandler(filters.PHOTO, handle_barcode_photo))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_food_message))

    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

def cancel_active_requests(context):
    keys_to_cancel = [
        "awaiting_weight",
        "awaiting_barcode_amount",
        "pending_barcode_product",
        "awaiting_clear_today_confirm",
        "history_start",
        "changing_language_only",
        "calories_goal",
    ]

    for key in keys_to_cancel:
        if key in context.user_data:
            context.user_data.pop(key, None)

if __name__ == "__main__":
    main()


