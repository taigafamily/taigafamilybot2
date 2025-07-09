from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

BOT_TOKEN = "7767900402:AAHsRjDChEL83frntnxkN3coswjP9sbX0Rg"
ADMIN_ID = 5676657478

bookings = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Забронировать", callback_data="book")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать в кальянную Тайга Family! 🔥\n"
        "Нажмите кнопку ниже, чтобы сделать бронь:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    booking_info = f"👤 {user.first_name} (@{user.username or 'без username'}) забронировал столик."

    bookings.append(booking_info)

    await query.edit_message_text("✅ Ваша бронь принята! Мы вас ждём 🙌")
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"📥 Новая бронь:\n{booking_info}")

async def show_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔️ У вас нет доступа к этой команде.")
        return

    if bookings:
        text = "\n\n".join(bookings)
        await update.message.reply_text(f"📋 Все брони:\n\n{text}")
    else:
        await update.message.reply_text("⛔️ Пока нет броней.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bookings", show_bookings))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()