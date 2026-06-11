from telegram import Update
from telegram.ext import ContextTypes

from custom_food_service import estimate_custom_food, save_custom_food
from menu_service import food_keyboard
from settings_service import get_language


async def handle_custom_food_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    language = get_language(update.effective_user.id) or "fa"
    context.user_data["custom_food_name"] = text
    context.user_data["awaiting_custom_food_name"] = False
    context.user_data["awaiting_custom_food_ingredients"] = True

    await update.message.reply_text(
        "مواد تشکیل‌دهنده و مقدارها را بنویس:\n\nمثال:\n500 گرم آرد کامل\n200 گرم ماست یونانی\n2 عدد تخم مرغ"
        if language == "fa"
        else
        "Send the ingredients and amounts:\n\nExample:\n500g whole flour\n200g Greek yogurt\n2 eggs"
    )
    return

async def handle_custom_food_ingredients(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    language = get_language(update.effective_user.id) or "fa"
    food_name = context.user_data.get("custom_food_name")
    ingredients_text = text

    await update.message.reply_text(
        "در حال تخمین ارزش غذایی..."
        if language == "fa"
        else
        "Estimating nutrition..."
    )

    try:
        result = estimate_custom_food(food_name, ingredients_text)

        context.user_data["pending_custom_food"] = result
        context.user_data["awaiting_custom_food_ingredients"] = False
        context.user_data["awaiting_custom_food_confirm"] = True

        msg = (
            f"نتیجه تخمینی برای {result['food_name']}:\n\n"
            f"در هر 100 گرم:\n"
            f"🔥 کالری: {result['calories_per_100g']}\n"
            f"💪 پروتئین: {result['protein_per_100g']} گرم\n\n"
            f"ذخیره کنم؟\n"
            f"بله / نه"
            if language == "fa"
            else
            f"Estimated result for {result['food_name']}:\n\n"
            f"Per 100g:\n"
            f"🔥 Calories: {result['calories_per_100g']}\n"
            f"💪 Protein: {result['protein_per_100g']}g\n\n"
            f"Save it?\n"
            f"YES / NO"
        )

        await update.message.reply_text(msg)

    except Exception as e:
        print("CUSTOM FOOD ERROR:", repr(e), flush=True)

        await update.message.reply_text(
            "نتونستم تخمین بزنم. لطفاً مواد را واضح‌تر بنویس."
            if language == "fa"
            else
            "I couldn't estimate it. Please write the ingredients more clearly."
        )

        context.user_data["awaiting_custom_food_ingredients"] = False
        context.user_data.pop("custom_food_name", None)

    return

async def handle_custom_food_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    language = get_language(update.effective_user.id) or "fa"
    if text in ["بله", "YES", "Yes", "yes"]:
        result = context.user_data.get("pending_custom_food")

        if result:
            save_custom_food(
                result["food_name"],
                result["calories_per_100g"],
                result["protein_per_100g"],
            )

            msg = (
                f"✅ ذخیره شد.\n\nاز این به بعد می‌تونی بنویسی:\n100 گرم {result['food_name']}"
                if language == "fa"
                else
                f"✅ Saved.\n\nNow you can write:\n100g {result['food_name']}"
            )
        else:
            msg = "چیزی برای ذخیره پیدا نشد." if language == "fa" else "Nothing found to save."

        context.user_data["awaiting_custom_food_confirm"] = False
        context.user_data.pop("pending_custom_food", None)
        context.user_data.pop("custom_food_name", None)

        await update.message.reply_text(msg, reply_markup=food_keyboard(language))
        return

    if text in ["نه", "NO", "No", "no"]:
        context.user_data["awaiting_custom_food_confirm"] = False
        context.user_data.pop("pending_custom_food", None)
        context.user_data.pop("custom_food_name", None)

        await update.message.reply_text(
            "لغو شد." if language == "fa" else "Cancelled.",
            reply_markup=food_keyboard(language)
        )
        return

    await update.message.reply_text(
        "لطفاً بله یا نه بنویس."
        if language == "fa"
        else
        "Please answer YES or NO."
    )
    return

