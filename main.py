import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode



ADMIN_ID = 6202982315  # Замените на ваш Telegram ID
TOKEN = '7439369007:AAEkiULHkV0t1cguVZtB-0at-Z6F0AUkVDY'  # Вставьте токен вашего бота

def load_tasks(filename="tasks.json"):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

tasks = load_tasks()
user_progress = {}

# Отправка задания
async def send_task(context, user_id):
    step = user_progress.get(user_id, 0)
    if step >= len(tasks):
        await context.bot.send_message(chat_id=user_id, text="Квест завершён! 🏁💫\nТы прошла весь квест!💘\nСпасибо за каждый момент этого волшебного путешествия — я безмерно люблю тебя  💖 ")
        return

    task = tasks[step]
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Подтвердить задание", callback_data=f"approve_{user_id}")]])
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"Пользователь {user_id} выполняет:\n\nЗадание {step + 1}: {task['title']}", reply_markup=keyboard)

    if task["type"] == "choice":
        for opt in task["options"]:
            with open(opt["image"], "rb") as img:
                await context.bot.send_photo(chat_id=user_id, photo=img, caption=opt["caption"])
        await context.bot.send_message(chat_id=user_id, text=task["prompt"])
    else:
        await context.bot.send_message(chat_id=user_id, text=task["prompt"], parse_mode=ParseMode.HTML)

# Обработка команды /start с параметром
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_progress:
        user_progress[user_id] = 0

    step = user_progress.get(user_id, 0)
    if step >= len(tasks):
        await update.message.reply_text("Квест завершён! 🏁💫\nТы прошла весь квест!💘\nСпасибо за каждый момент этого волшебного путешествия — я безмерно люблю тебя  💖")
        return

    task = tasks[step]

    # Если QR-задание и аргумент qr
    if task["type"] == "qr" and context.args and context.args[0].lower() == "qr":
        await update.message.reply_text(task["success"])
        user_progress[user_id] += 1
        await send_task(context, user_id)
        return

    await update.message.reply_text(
        "Доброе утро, моя любовь! ☀️💋\nСегодня у нас с тобой особенный день, полный сюрпризов, нежности и волшебства ✨\nНаше приключение начинается прямо сейчас… Готова? 💖",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Начать", callback_data="start_quest")]])
    )

# Обработка кнопок
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start_quest":
        await send_task(context, query.from_user.id)

    elif query.data.startswith("approve_"):
        uid = int(query.data.split("_")[1])
        task = tasks[user_progress[uid]]
        await context.bot.send_message(chat_id=uid, text=task["success"])
        user_progress[uid] += 1
        await send_task(context, uid)

# Обработка текстовых сообщений (например, загадок)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    step = user_progress.get(user_id, 0)
    if step >= len(tasks):
        return

    task = tasks[step]
    user_text = update.message.text.strip().lower()

    if task["type"] == "riddle":
        if user_text == task["answer"]:
            await context.bot.send_message(chat_id=user_id, text=task["success"])
            user_progress[user_id] += 1
            await send_task(context, user_id)
        else:
            await context.bot.send_message(chat_id=user_id, text="Неправильный ответ. Попробуй ещё раз.")

# Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()
