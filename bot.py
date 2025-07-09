import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, ContextTypes,
                          MessageHandler, filters, ConversationHandler, CallbackQueryHandler)
from datetime import datetime, timedelta

BOT_TOKEN = "7767900402:AAHsRjDChEL83frntnxkN3coswjP9sbX0Rg"
ADMIN_ID = 5676657478
BOOKINGS_FILE = "bookings.json"

NAME, GUESTS, DATE, TIME, PHONE = range(5)

try:
    with open(BOOKINGS_FILE, "r", encoding="utf-8") as f:
        bookings = json.load(f)
except FileNotFoundError:
    bookings = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌿 *Добро пожаловать в кальянную Тайга Family!* 🌿\n\n"
        "Чтобы забронировать столик, нажмите /book",
        parse_mode="Markdown"
    )

async def book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 *Как вас зовут?*", parse_mode="Markdown")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("👥 *Сколько гостей?*", parse_mode="Markdown")
    return GUESTS

async def get_guests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["guests"] = update.message.text
    await show_calendar(update, context)
    return DATE

async def show_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now()
    keyboard = []
    for i in range(7):
        day = today + timedelta(days=i)
        button = InlineKeyboardButton(
            text=day.strftime("📅 %d.%m.%Y (%a)"),
            callback_data=f"date_{day.strftime('%Y-%m-%d')}"
        )
        keyboard.append([button])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📅 *Выберите дату бронирования:*",
                                    reply_markup=reply_markup, parse_mode="Markdown")

async def select_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    date_str = query.data.split("_")[1]
    context.user_data["date"] = date_str
    await show_time_picker(query, context)
    return TIME

async def show_time_picker(query, context):
    times = ["18:00", "19:00", "20:00", "21:00", "22:00"]
    keyboard = [[InlineKeyboardButton(t, callback_data=f"time_{t}")] for t in times]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("⏰ *Выберите время бронирования:*",
                                  reply_markup=reply_markup, parse_mode="Markdown")

async def select_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    time_str = query.data.split("_")[1]
    context.user_data["time"] = time_str
    await query.edit_message_text(
        f"📅 Дата: *{context.user_data['date']}*\n"
        f"⏰ Время: *{context.user_data['time']}*",
        parse_mode="Markdown"
    )
"
                                  f"⏰ Время: *{context.user_data['time']}*", parse_mode="Markdown")
    await query.message.reply_text("📞 *Ваш телефон?*\n_Можно пропустить_", parse_mode="Markdown")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    booking = {
        "user_id": update.effective_user.id,
        "name": context.user_data["name"],
        "guests": context.user_data["guests"],
        "datetime": f"{context.user_data['date']} {context.user_data['time']}",
        "phone": context.user_data["phone"],
        "status": "⏳ В ожидании"
    }
    bookings.append(booking)
    save_bookings()

    text = (f"📥 *Новая бронь!*\n"
            f"👤 *Имя:* {booking['name']}\n"
            f"👥 *Гостей:* {booking['guests']}\n"
            f"📅 *Дата/время:* {booking['datetime']}\n"
            f"📞 *Телефон:* {booking['phone']}\n"
            f"━━━━━━━━━━━━━━")
    keyboard = [
        [InlineKeyboardButton("✅ Принять", callback_data=f"accept_{len(bookings)-1}"),
         InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{len(bookings)-1}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=ADMIN_ID, text=text, reply_markup=reply_markup, parse_mode="Markdown")

    await update.message.reply_text(
        "✅ *Ваша заявка отправлена!*\n⏳ Ожидайте подтверждения от администратора.",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

def save_bookings():
    with open(BOOKINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(bookings, f, ensure_ascii=False, indent=2)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    index = int(data.split("_")[1])
    booking = bookings[index]

    if data.startswith("accept"):
        booking["status"] = "✅ Принята"
        text = "🎉 *Ваша бронь подтверждена!*\nДо встречи в Тайга Family!"
    elif data.startswith("reject"):
        booking["status"] = "❌ Отклонена"
        text = "😔 *К сожалению, ваша бронь отклонена.*"

    save_bookings()
    await context.bot.send_message(chat_id=booking["user_id"], text=text, parse_mode="Markdown")
    await query.edit_message_text(f"{query.message.text}\n\n*Статус:* {booking['status']}", parse_mode="Markdown")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("book", book)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GUESTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_guests)],
            DATE: [CallbackQueryHandler(select_date, pattern="^date_")],
            TIME: [CallbackQueryHandler(select_time, pattern="^time_")],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)]
        },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()