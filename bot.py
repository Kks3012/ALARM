import telebot
from telebot import types
import requests
import json
import os

# --- КОНФІГУРАЦІЯ БОТА ---
# Отримайте свій токен бота від @BotFather у Telegram
TELEGRAM_BOT_TOKEN = "7955277234:AAEhoBFDQcawuISjbJ_ZBiaD8Ctw5ko1ONg"
# Отримайте свій Telegram ID користувача (наприклад, через @userinfobot),
# щоб лише ви могли керувати ботом. Це число.
AUTHORIZED_USER_ID = 5244460157 # ВСТАВТЕ_СВІЙ_ТЕЛЕГРАМ_ID_СЮДИ (як число)
# URL до вашого застосунку на Windows. Якщо бот і застосунок на одному ПК, залиште 127.0.0.1
# Якщо на різних, замініть 127.0.0.1 на IP-адресу ПК з Windows-застосунком.
WINDOWS_APP_URL = "http://127.0.0.1:5000"
# --- КІНЕЦЬ КОНФІГУРАЦІЇ ---

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Глобальні змінні для відстеження стану автоматичних режимів на стороні бота.
# Фактичний стан контролюється Windows-застосунком.
AUTO_MINUTE_OF_SILENCE_ENABLED = True
AUTO_ALARM_ENABLED = False # Функціонал для авто-тривоги поки не реалізовано в Windows-апп

# Функція для перевірки, чи користувач авторизований
def is_authorized(message):
    return str(message.from_user.id) == str(AUTHORIZED_USER_ID)

# Функція для відправки команд на Windows-застосунок
def send_command_to_windows_app(chat_id, command_type):
    payload = {"command": command_type}
    try:
        response = requests.post(f"{WINDOWS_APP_URL}/command", json=payload, timeout=5) # Додаємо таймаут
        if response.status_code == 200:
            bot.send_message(chat_id, f"Команда '{command_type}' успішно відправлена.")
            # Для команд зміни авто-режиму, оновлюємо стан бота
            # Оголошення global тут має бути перед першим присвоєнням
            global AUTO_MINUTE_OF_SILENCE_ENABLED # Оголошуємо global тут
            global AUTO_ALARM_ENABLED # Оголошуємо global тут

            if command_type == 'enable_auto_minute_of_silence':
                AUTO_MINUTE_OF_SILENCE_ENABLED = True
            elif command_type == 'disable_auto_minute_of_silence':
                AUTO_MINUTE_OF_SILENCE_ENABLED = False
            elif command_type == 'enable_auto_alarm': # Якщо буде реалізовано
                AUTO_ALARM_ENABLED = True
            elif command_type == 'disable_auto_alarm': # Якщо буде реалізовано
                AUTO_ALARM_ENABLED = False
        else:
            bot.send_message(chat_id, f"Помилка при відправці команди '{command_type}': {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        bot.send_message(chat_id, "Не вдалося підключитися до застосунку на Windows. Переконайтеся, що він запущений і доступний за адресою.")
    except requests.exceptions.Timeout:
        bot.send_message(chat_id, "Таймаут підключення до застосунку на Windows. Можливо, він зайнятий або недоступний.")
    except Exception as e:
        bot.send_message(chat_id, f"Виникла невідома помилка при відправці команди: {e}")

# --- МЕНЮ ТА КНОПКИ ---

def main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn_minute = types.KeyboardButton("Хвилина Мовчання 🕯️")
    btn_alarm = types.KeyboardButton("Тривога 🚨")
    markup.add(btn_minute, btn_alarm)
    bot.send_message(chat_id, "Оберіть розділ:", reply_markup=markup)

def minute_of_silence_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn_auto = types.KeyboardButton("Автоматичний режим (Хвилина) 🔄")
    btn_manual = types.KeyboardButton("Ручний режим (Хвилина) 🖐️")
    btn_back = types.KeyboardButton("◀️ Назад до головного меню")
    markup.add(btn_auto, btn_manual)
    markup.add(btn_back)
    bot.send_message(chat_id, "Оберіть режим для Хвилини Мовчання:", reply_markup=markup)

def alarm_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn_auto = types.KeyboardButton("Автоматичний режим (Тривога) 🔄")
    btn_manual = types.KeyboardButton("Ручний режим (Тривога) 🖐️")
    btn_back = types.KeyboardButton("◀️ Назад до головного меню")
    markup.add(btn_auto, btn_manual)
    markup.add(btn_back)
    bot.send_message(chat_id, "Оберіть режим для Тривоги:", reply_markup=markup)

def manual_minute_of_silence_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn_play = types.KeyboardButton("Запустити Хвилину Мовчання негайно ▶️")
    btn_stop = types.KeyboardButton("Припинити все ⏹️")
    btn_back = types.KeyboardButton("◀️ Назад до Хвилини Мовчання")
    markup.add(btn_play)
    markup.add(btn_stop)
    markup.add(btn_back)
    bot.send_message(chat_id, "Ручне управління Хвилиною Мовчання:", reply_markup=markup)

def manual_alarm_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn_alarm_on = types.KeyboardButton("Запустити Тривогу 🔔")
    btn_alarm_off = types.KeyboardButton("Відбій Тривоги ✅")
    btn_stop = types.KeyboardButton("Припинити все ⏹️")
    btn_back = types.KeyboardButton("◀️ Назад до Тривоги")
    markup.add(btn_alarm_on, btn_alarm_off)
    markup.add(btn_stop)
    markup.add(btn_back)
    bot.send_message(chat_id, "Ручне управління Тривогою:", reply_markup=markup)

def auto_minute_of_silence_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    status_text = "Увімкнено ✅" if AUTO_MINUTE_OF_SILENCE_ENABLED else "Вимкнено ❌"
    btn_toggle = types.KeyboardButton(f"Перемкнути автозапуск (зараз: {status_text})")
    btn_back = types.KeyboardButton("◀️ Назад до Хвилини Мовчання")
    markup.add(btn_toggle)
    markup.add(btn_back)
    bot.send_message(chat_id, f"Автоматичний режим 'Хвилина Мовчання' (щодня о 08:59).\nСтатус: {status_text}", reply_markup=markup)

def auto_alarm_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    status_text = "Увімкнено ✅" if AUTO_ALARM_ENABLED else "Вимкнено ❌"
    btn_toggle = types.KeyboardButton(f"Перемкнути автозапуск (зараз: {status_text})")
    btn_back = types.KeyboardButton("◀️ Назад до Тривоги")
    markup.add(btn_toggle)
    markup.add(btn_back)
    bot.send_message(chat_id, f"Автоматичний режим 'Тривога' (функціонал у розробці).\nСтатус: {status_text}", reply_markup=markup)

# --- ОБРОБНИКИ КОМАНД ТА ТЕКСТУ ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_authorized(message):
        bot.reply_to(message, "Ви не авторизовані для використання цього бота.")
        return
    bot.reply_to(message, "Привіт! Я бот для системи оповіщення. Оберіть дію:")
    main_menu(message.chat.id)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not is_authorized(message):
        bot.reply_to(message, "Ви не авторизовані для використання цього бота.")
        return

    # Оголошення глобальних змінних має бути на початку функції, якщо ви плануєте їх змінювати
    global AUTO_MINUTE_OF_SILENCE_ENABLED
    global AUTO_ALARM_ENABLED

    text = message.text

    if text == "Хвилина Мовчання 🕯️":
        minute_of_silence_menu(message.chat.id)
    elif text == "Тривога 🚨":
        alarm_menu(message.chat.id)
    elif text == "Автоматичний режим (Хвилина) 🔄":
        auto_minute_of_silence_menu(message.chat.id)
    elif text == "Ручний режим (Хвилина) 🖐️":
        manual_minute_of_silence_menu(message.chat.id)
    elif text == "Автоматичний режим (Тривога) 🔄":
        auto_alarm_menu(message.chat.id)
    elif text == "Ручний режим (Тривога) 🖐️":
        manual_alarm_menu(message.chat.id)
    elif text == "◀️ Назад до головного меню":
        main_menu(message.chat.id)
    elif text == "◀️ Назад до Хвилини Мовчання":
        minute_of_silence_menu(message.chat.id)
    elif text == "◀️ Назад до Тривоги":
        alarm_menu(message.chat.id)
    # Ручні команди відтворення/зупинки
    elif text == "Запустити Хвилину Мовчання негайно ▶️":
        send_command_to_windows_app(message.chat.id, "play_minute_of_silence")
    elif text == "Запустити Тривогу 🔔":
        send_command_to_windows_app(message.chat.id, "play_alarm")
    elif text == "Відбій Тривоги ✅":
        send_command_to_windows_app(message.chat.id, "play_all_clear")
    elif text == "Припинити все ⏹️":
        send_command_to_windows_app(message.chat.id, "stop_all_sounds")
    # Перемикання автоматичних режимів
    elif text.startswith("Перемкнути автозапуск (зараз:"):
        # Перевіряємо, яка кнопка була натиснута, щоб оновити правильний стан
        if "Хвилина)" in text:
            AUTO_MINUTE_OF_SILENCE_ENABLED = not AUTO_MINUTE_OF_SILENCE_ENABLED
            command = "enable_auto_minute_of_silence" if AUTO_MINUTE_OF_SILENCE_ENABLED else "disable_auto_minute_of_silence"
            send_command_to_windows_app(message.chat.id, command)
            # Оновлюємо меню після зміни стану
            auto_minute_of_silence_menu(message.chat.id)
        elif "Тривога)" in text:
            AUTO_ALARM_ENABLED = not AUTO_ALARM_ENABLED
            command = "enable_auto_alarm" if AUTO_ALARM_ENABLED else "disable_auto_alarm"
            send_command_to_windows_app(message.chat.id, command)
            # Оновлюємо меню після зміни стану
            auto_alarm_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Невідома команда. Будь ласка, оберіть зі списку або натисніть /start.")

print("Бот запущено. Очікую команди...")
bot.polling(none_stop=True)