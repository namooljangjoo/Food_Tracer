from telegram import Update
from telegram.ext import ContextTypes

from chart_service import generate_weight_chart
from menu_service import main_keyboard
from settings_service import get_language
from weight_service import save_weight, get_weight_history


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

    chart_path = generate_weight_chart(user_id)

    if not chart_path:
        msg = (
            "At least 2 weight entries are required."
            if language == "en"
            else "حداقل ۲ ثبت وزن لازم است."
        )

        await update.message.reply_text(msg)
        return

    with open(chart_path, "rb") as chart:
        await update.message.reply_photo(
            photo=chart,
            caption=(
                "📈 Weight Progress"
                if language == "en"
                else "📈 روند وزن"
            ),
        )
