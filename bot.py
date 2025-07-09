import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
)

# Вшитые токен и админ ID
BOT_TOKEN = "7767900402:AAHsRjDChEL83frntnxkN3coswjP9sbX0Rg"
ADMIN_ID = 5676657478

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Хэндлеры
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📅 Забронировать столик", callback_data="book")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Добро пожаловать в Taiga Family! 🌿
Нажмите кнопку ниже, чтобы забронировать столик:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "book":
        keyboard = [
            [InlineKeyboardButton("Сегодня 📅", callback_data="date_today"),
             InlineKeyboardButton("Завтра 📅", callback_data="date_tomorrow")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите дату бронирования:", reply_markup=reply_markup)
    elif query.data.startswith("date_"):
        context.user_data["date"] = "Сегодня" if query.data == "date_today" else "Завтра"
        keyboard = [
            [InlineKeyboardButton("18:00 ⏰", callback_data="time_18"),
             InlineKeyboardButton("19:00 ⏰", callback_data="time_19")],
            [InlineKeyboardButton("20:00 ⏰", callback_data="time_20"),
             InlineKeyboardButton("21:00 ⏰", callback_data="time_21")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите время:", reply_markup=reply_markup)
    elif query.data.startswith("time_"):
        context.user_data["time"] = query.data.replace("time_", "") + ":00"
        keyboard = [
            [InlineKeyboardButton("2 👥", callback_data="guests_2"),
             InlineKeyboardButton("4 👥", callback_data="guests_4")],
            [InlineKeyboardButton("6 👥", callback_data="guests_6"),
             InlineKeyboardButton("8 👥", callback_data="guests_8")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Сколько гостей будет?", reply_markup=reply_markup)
    elif query.data.startswith("guests_"):
        context.user_data["guests"] = query.data.replace("guests_", "")
        text = (
            f"📅 Дата: {context.user_data['date']}
"
            f"⏰ Время: {context.user_data['time']}
"
            f"👥 Гостей: {context.user_data['guests']}

"
            "✅ Ваша бронь принята!"
        )
        await query.edit_message_text(text)
        # Отправляем админу
        admin_message = (
            f"🔔 Новая бронь!
"
            f"👤 @{query.from_user.username or query.from_user.first_name}
"
            f"📅 Дата: {context.user_data['date']}
"
            f"⏰ Время: {context.user_data['time']}
"
            f"👥 Гостей: {context.user_data['guests']}"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    logger.info("Taiga Family Bot запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
