import telebot
from telebot import types
from datetime import datetime, timedelta
import json
import subprocess

# 🔑 Вставь токен от BotFather
TOKEN = ''
bot = telebot.TeleBot(TOKEN)

# 📁 Загрузи афишу один раз при запуске
with open('events_with_parsed.json', encoding='utf-8') as f:
    EVENTS = json.load(f)

# 🛠 Вспомогательная функция
def filter_events(start_date, end_date):
    filtered = []
    for event in EVENTS:
        for date_str in event.get("parsed_dates", []):
            dt = datetime.fromisoformat(date_str)
            if start_date <= dt <= end_date:
                filtered.append({
                    "title": event["title"],
                    "description": event["description"],
                    "date": dt.strftime("%d.%m.%Y %H:%M"),
                    "image": event.get("image", ""),
                    "ticket_link": event.get("ticket_link", "")
                })
                break
    return filtered

def send_events(chat_id, events):
    if not events:
        bot.send_message(chat_id, "😔 Нет мероприятий в выбранный период.")
        return

    for event in events:
        caption = f"<b>{event['title']}</b>\n\n🕒 <i>{event['date']}</i>\n\n{event['description']}"
        markup = types.InlineKeyboardMarkup()
        if event['ticket_link']:
            markup.add(types.InlineKeyboardButton("🎫 Купить билет", url=event['ticket_link']))
        try:
            bot.send_photo(chat_id, photo=event['image'], caption=caption, parse_mode='HTML', reply_markup=markup)
        except Exception:
            bot.send_message(chat_id, caption, parse_mode='HTML', reply_markup=markup)

# 🎛 Главное меню
def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("🎵 На этой неделе")
    btn2 = types.KeyboardButton("🔜 На следующей неделе")
    btn3 = types.KeyboardButton("📅 В этом месяце")
    btn4 = types.KeyboardButton("📆 Указать диапазон дат")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(chat_id, "Выберите за какой период показать мероприятия:", reply_markup=markup)

# 🎉 Обработка /start
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}! 👋\nЯ бот афиши Забайкальской краевой филармонии.")
    show_main_menu(message.chat.id)

# ℹ️ Помощь
@bot.message_handler(commands=['help'])
def help_handler(message):
    help_text = (
        "📌 Я могу показать тебе предстоящие концерты в Забайкальской краевой филармонии!\n\n"
        "Вот что я умею:\n"
        "🔹 /start — начать работу\n"
        "🔹 /help — показать эту справку\n\n"
        "📅 Выбери период на кнопках, чтобы посмотреть мероприятия 🎶"
    )
    bot.send_message(message.chat.id, help_text)

# 📩 Обработка всех сообщений
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text.lower()
    today = datetime.today()
    subprocess.run(["python3", "parserimag.py"])

    if text in ("начать", "start", "/начать"):
        start_handler(message)

    elif "на этой неделе" in text:
        start_date = today
        end_date = today + timedelta(days=6 - today.weekday())
        events = filter_events(start_date, end_date)
        send_events(message.chat.id, events)

    elif "на следующей неделе" in text:
        start_date = today + timedelta(days=(7 - today.weekday()))
        end_date = start_date + timedelta(days=6)
        events = filter_events(start_date, end_date)
        send_events(message.chat.id, events)

    elif "в этом месяце" in text:
        start_date = today.replace(day=1)
        next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        end_date = next_month - timedelta(days=1)
        events = filter_events(start_date, end_date)
        send_events(message.chat.id, events)

    elif "указать диапазон" in text:
        bot.send_message(message.chat.id, "📆 Введите диапазон в формате `дд.мм.гггг-дд.мм.гггг`")

    elif "-" in text:
        try:
            parts = text.replace(" ", "").split("-")
            start_date = datetime.strptime(parts[0], "%d.%m.%Y")
            end_date = datetime.strptime(parts[1], "%d.%m.%Y")
            events = filter_events(start_date, end_date)
            send_events(message.chat.id, events)
        except Exception:
            bot.send_message(message.chat.id, "❌ Неверный формат. Попробуйте: `дд.мм.гггг-дд.мм.гггг`")

    else:
        # Отправляем кнопку "Начать" при первом сообщении
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Начать"))
        bot.send_message(message.chat.id, "👋 Привет! Чтобы начать, нажми кнопку ниже 👇", reply_markup=markup)

# ▶️ Запуск бота
print("Бот запущен...")
bot.polling(none_stop=True)
