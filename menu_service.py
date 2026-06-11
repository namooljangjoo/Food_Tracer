from telegram import ReplyKeyboardMarkup


def main_keyboard(language="fa"):
    if language == "en":
        keyboard = [
            ["🍽 Food", "📊 Reports"],
            ["⚙️ Settings", "ℹ️ More"],
        ]
    else:
        keyboard = [
            ["🍽 غذا", "📊 گزارش‌ها"],
            ["⚙️ تنظیمات", "ℹ️ بیشتر"],
        ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def food_keyboard(language="fa"):
    if language == "en":
        keyboard = [
            ["➕ Log Food"],
            ["➕ Custom Food"],
            ["📸 Food Photo"],
            ["⭐ Save Favorite"],
            ["⭐ Favorites"],
            ["📦 Scan Barcode"],
            ["↩️ Undo Last Meal"],
            ["⬅️ Back"],
        ]
    else:
        keyboard = [
            ["➕ ثبت غذا"],
            ["➕ غذای سفارشی"],
            ["📸 عکس غذا"],
            ["⭐ ذخیره محبوب"],
            ["⭐ غذاهای محبوب"],
            ["📦 اسکن بارکد"],
            ["↩️ حذف آخرین غذا"],
            ["⬅️ بازگشت"],
        ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def reports_keyboard(language="fa"):
    if language == "en":
        keyboard = [
            ["📅 Today"],
            ["🎯 Today Progress"],
            ["🎯 Adaptive Goal"],
            ["📈 Weekly Report"],
            ["🛒 Shopping List"],
            ["🍱 Meal Plan"],
            ["🧠 Nutrition Analysis"],
            ["🧠 My Coach"],
            ["⚖️ Weight Trend"],
            ["⬅️ Back"],
        ]
    else:
        keyboard = [
            ["📅 امروز"],
            ["🎯 پیشرفت امروز"],
            ["🎯 پیشنهاد هدف"],
            ["📈 گزارش هفتگی"],
            ["🛒 لیست خرید"],
            ["🍱 برنامه غذایی"],
            ["🧠 تحلیل تغذیه"],
            ["🧠 مربی من"],
            ["⚖️ روند وزن"],
            ["⬅️ بازگشت"],
        ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def settings_keyboard(language="fa"):
    if language == "en":
        keyboard = [
            ["🎯 Goals"],
            ["🌍 Language"],
            ["⚖️ Log Weight"],
            ["⬅️ Back"],
        ]
    else:
        keyboard = [
            ["🎯 اهداف"],
            ["🌍 زبان"],
            ["⚖️ ثبت وزن"],
            ["⬅️ بازگشت"],
        ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def more_keyboard(language="fa"):
    if language == "en":
        keyboard = [
            ["📜 History"],
            ["ℹ️ About"],
            ["⬅️ Back"],
        ]
    else:
        keyboard = [
            ["📜 تاریخچه"],
            ["ℹ️ درباره"],
            ["⬅️ بازگشت"],
        ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
