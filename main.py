import os
import pickle
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import asyncio

import config

# Файл для хранения ID пользователей
USER_DATA_FILE = "user_data.pkl"


# Загрузка данных пользователей из файла
def load_user_ids():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'rb') as file:
            return pickle.load(file)
    return set()


# Сохранение данных пользователей в файл
def save_user_ids(user_ids):
    with open(USER_DATA_FILE, 'wb') as file:
        pickle.dump(user_ids, file)


# Список для хранения ID пользователей
user_ids = load_user_ids()


# Функция обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if user_id not in user_ids:
        user_ids.add(user_id)
        save_user_ids(user_ids)  # Сохранение после добавления пользователя
    await update.message.reply_text(text="Привет!👋 Меня зовут Спыну Марианна, я дипломированный\n"
                                                         "психоаналитик с 15-летним опытом работы. Я помогаю людям\n"
                                                         "разобраться в сложных эмоциональных переживаниях и\n"
                                                         "обрести внутреннюю гармонию.\n\n"
                                                         "*Тема вебинара:*\n"
                                                         "Сильно люблю мужа, но всегда есть желание уйти.\n"
                                                         "Почему возникают такие противоречия и как с ними справиться?\n"
                                                         "\n"
                                                         "На вебинаре мы обсудим:\n"
                                                         "💬 Природу внутренних конфликтов в отношениях.\n"
                                                         "💬 Возможные причины возникновения противоречивых чувств.\n"
                                                         "💬 Как обрести баланс между любовью и личной свободой.\n\n"
                                                         "Вебинар пройдет *12 сентября в 20:00.*\n"
                                                         "Я обязательно напомню вам о нем!\n\n"
                                                         "Буду рада вам помочь разобраться в этом вопросе!"
                                   ,parse_mode="Markdown")


# Функция для отправки уведомлений всем пользователям в заданную дату
async def send_notifications(context: ContextTypes.DEFAULT_TYPE):
    for user_id in user_ids:
        await context.bot.send_message(chat_id=user_id, text="Напоминание! Сегодня 12 сентября 2024 года!")


# Функция для отправки тестового уведомления одному пользователю через минуту
async def send_test_notification(context: ContextTypes.DEFAULT_TYPE):
    user_id = context.job.data
    await context.bot.send_message(chat_id=user_id, text="Привет!👋 Меня зовут Спыну Марианна, я дипломированный\n"
                                                         "психоаналитик с 15-летним опытом работы. Я помогаю людям\n"
                                                         "разобраться в сложных эмоциональных переживаниях и\n"
                                                         "обрести внутреннюю гармонию.\n\n"
                                                         "**Тема вебинара:**\n"
                                                         "Сильно люблю мужа, но всегда есть желание уйти.\n"
                                                         "Почему возникают такие противоречия и как с ними справиться?\n"
                                                         "\n"
                                                         "На вебинаре мы обсудим:\n"
                                                         "💬 Природу внутренних конфликтов в отношениях.\n"
                                                         "💬 Возможные причины возникновения противоречивых чувств.\n"
                                                         "💬 Как обрести баланс между любовью и личной свободой.\n\n"
                                                         "Вебинар пройдет **12 сентября в 20:00.**\n"
                                                         "Я обязательно напомню вам о нем!\n\n"
                                                         "Буду рада вам помочь разобраться в этом вопросе!"
                                   ,parse_mode="Markdown"
                                   )


# Функция обработчик команды /test
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    await update.message.reply_text("Тестовое уведомление будет отправлено через 1 минуту.")

    # Планируем отправку уведомления через 1 минуту
    context.job_queue.run_once(send_test_notification, timedelta(minutes=1), data=user_id)


if __name__ == '__main__':
    # Инициализация бота с вашим токеном
    application = ApplicationBuilder().token(config.TOKEN).build()

    # Добавляем обработчики команд /start и /test
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test", test))

    # Планировщик задач для отправки уведомлений всем пользователям
    scheduler = BackgroundScheduler()

    # Запланировать задачу на 12 сентября 2024 года в 09:00 (или любое другое время)
    run_date = datetime(2024, 9, 12, 9, 0, 0)  # Укажите нужную дату и время
    scheduler.add_job(lambda: application.create_task(send_notifications(None)), 'date', run_date=run_date)

    # Запуск планировщика
    scheduler.start()

    print("Бот запущен")
    application.run_polling()
