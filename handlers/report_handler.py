import os

from telegram import Update
from telegram.ext import ContextTypes

from adaptive_goal_service import get_adaptive_goal_suggestion
from analysis_formatter import format_analysis
from analysis_service import analyze_nutrition
from chart_service import create_weekly_chart
from daily_summary import get_today_summary, get_today_foods
from localization_service import translate_food_name
from menu_service import main_keyboard, reports_keyboard
from progress_service import get_today_progress
from report_service import get_weekly_report
from settings_service import get_language
from shopping_service import generate_weekly_shopping_list


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
async def today_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"

    progress = get_today_progress(user_id)

    if not progress:
        text = (
            "No daily goal is set."
            if language == "en"
            else "هدف روزانه هنوز تنظیم نشده."
        )
        await update.message.reply_text(text, reply_markup=reports_keyboard(language))
        return

    if language == "en":
        text = (
            "🎯 Today Progress\n\n"
            "🔥 Calories\n"
            f"{progress['total_calories']} / {progress['calories_goal']} kcal\n"
            f"{progress['calories_bar']} {progress['calories_percent']}%\n\n"
            "💪 Protein\n"
            f"{progress['total_protein']} / {progress['protein_goal']}g\n"
            f"{progress['protein_bar']} {progress['protein_percent']}%"
        )
    else:
        text = (
            "🎯 پیشرفت امروز\n\n"
            "🔥 کالری\n"
            f"{progress['total_calories']} / {progress['calories_goal']} کالری\n"
            f"{progress['calories_bar']} {progress['calories_percent']}٪\n\n"
            "💪 پروتئین\n"
            f"{progress['total_protein']} / {progress['protein_goal']} گرم\n"
            f"{progress['protein_bar']} {progress['protein_percent']}٪"
        )

    await update.message.reply_text(text, reply_markup=reports_keyboard(language))
async def adaptive_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"

    suggestion = get_adaptive_goal_suggestion(user_id)

    if not suggestion:
        await update.message.reply_text(
            "هنوز هدف روزانه تنظیم نشده."
            if language == "fa"
            else "No daily goal is set.",
            reply_markup=reports_keyboard(language),
        )
        return

    if suggestion["type"] == "not_enough_data":
        await update.message.reply_text(
            f"برای پیشنهاد دقیق، حداقل ۴ روز ثبت غذا لازم است.\n"
            f"فعلاً فقط {suggestion['logged_days']} روز داده داری."
            if language == "fa"
            else
            f"At least 4 logged days are needed for a good suggestion.\n"
            f"You currently have {suggestion['logged_days']} logged days.",
            reply_markup=reports_keyboard(language),
        )
        return

    if suggestion["type"] == "no_change":
        await update.message.reply_text(
            (
                "🎯 هدف فعلی مناسب به نظر می‌رسد.\n\n"
                f"میانگین کالری: {suggestion['avg_calories']}\n"
                f"هدف کالری: {suggestion['current_calories']}\n\n"
                f"میانگین پروتئین: {suggestion['avg_protein']} گرم\n"
                f"هدف پروتئین: {suggestion['current_protein']} گرم"
            )
            if language == "fa"
            else
            (
                "🎯 Your current goal looks reasonable.\n\n"
                f"Average calories: {suggestion['avg_calories']}\n"
                f"Calorie goal: {suggestion['current_calories']}\n\n"
                f"Average protein: {suggestion['avg_protein']}g\n"
                f"Protein goal: {suggestion['current_protein']}g"
            ),
            reply_markup=reports_keyboard(language),
        )
        return

    context.user_data["pending_goal_suggestion"] = suggestion
    context.user_data["awaiting_goal_suggestion_confirm"] = True

    await update.message.reply_text(
        (
            "🎯 پیشنهاد تنظیم هدف\n\n"
            f"میانگین کالری ۷ روز اخیر: {suggestion['avg_calories']}\n"
            f"هدف کالری فعلی: {suggestion['current_calories']}\n"
            f"هدف کالری پیشنهادی: {suggestion['suggested_calories']}\n\n"
            f"میانگین پروتئین: {suggestion['avg_protein']} گرم\n"
            f"هدف پروتئین فعلی: {suggestion['current_protein']} گرم\n"
            f"هدف پروتئین پیشنهادی: {suggestion['suggested_protein']} گرم\n\n"
            "این تغییر را اعمال کنم؟\n"
            "بله / نه"
        )
        if language == "fa"
        else
        (
            "🎯 Adaptive Goal Suggestion\n\n"
            f"7-day average calories: {suggestion['avg_calories']}\n"
            f"Current calorie goal: {suggestion['current_calories']}\n"
            f"Suggested calorie goal: {suggestion['suggested_calories']}\n\n"
            f"Average protein: {suggestion['avg_protein']}g\n"
            f"Current protein goal: {suggestion['current_protein']}g\n"
            f"Suggested protein goal: {suggestion['suggested_protein']}g\n\n"
            "Apply this change?\n"
            "YES / NO"
        ),
        reply_markup=reports_keyboard(language),
    )

async def shopping_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_language(user_id) or "fa"
    foods = generate_weekly_shopping_list(user_id)

    if not foods:
        await update.message.reply_text(
            "هنوز غذای کافی ثبت نشده."
            if language == "fa"
            else "Not enough food data yet.",
            reply_markup=reports_keyboard(language),
        )
        return

    if language == "fa":
        msg = "🛒 لیست خرید پیشنهادی این هفته\n\n"
    else:
        msg = "🛒 Suggested Shopping List This Week\n\n"

    for item in foods:
        food_name = item["food_name"]
        amount = item["amount"]
        weekly_count = item["weekly_count"]

        if amount:
            msg += f"• {food_name}: {amount}\n"
        else:
            suffix = "بار" if language == "fa" else "times"
            msg += f"• {food_name} ({weekly_count} {suffix})\n"

    await update.message.reply_text(
        msg,
        reply_markup=reports_keyboard(language),
    )

    return

