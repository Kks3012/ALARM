import telebot
import requests
import os # <<< Додаємо імпорт модуля os
import time

# --- КОНФІГУРАЦІЯ БОТА ---
# Telegram Bot Token та Authorized User ID тепер будуть читатися зі змінних оточення!
# НЕ ЗАЛИШАЙТЕ ТОКЕН І ID В КОДІ НА GITHUB!
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Переконайтеся, що AUTHORIZED_USER_ID перетворюється на ціле число (int)
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID"))

# URL до вашого застосунку на Windows.
# Для локального запуску Windows-застосунку на тому ж ПК, що й бот (навіть якщо бот на Render),
# це залишається 127.0.0.1.
# Якщо ваш Windows-застосунок має бути доступний ззовні (наприклад, з Render),
# вам знадобиться публічна IP-адреса вашого ПК та/або налаштування переадресації портів на роутері.
# Наразі залишаємо так для тесту.
WINDOWS_APP_URL = "http://127.0.0.1:5000"

# Таймаут для запитів до застосунку Windows (у секундах)
REQUEST_TIMEOUT = 5
# --- КІНЕЦЬ КОНФІГУРАЦІЇ ---

# Перевірка, чи встановлено токен та ID
if not TELEGRAM_BOT_TOKEN:
    print("Помилка: TELEGRAM_BOT_TOKEN не встановлено у змінних оточення.")
    exit()
if not AUTHORIZED_USER_ID:
    print("Помилка: AUTHORIZED_USER_ID не встановлено у змінних оточення.")
    exit()

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Функція для надсилання команд застосунку на Windows
def send_command_to_windows_app(command):
    try:
        response = requests.post(
            f"{WINDOWS_APP_URL}/command",
            json={"command": command},
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status() # Викличе виняток для HTTP помилок (4xx або 5xx)
        print(f"Команда '{command}' успішно відправлена до застосунку Windows.")
        return True
    except requests.exceptions.Timeout:
        print(f"Помилка: Час очікування підключення до застосунку на Windows вичерпано для команди '{command}'.")
        return False
    except requests.exceptions.ConnectionError:
        print(f"Помилка: Не вдалося підключитися до застосунку на Windows за адресою {WINDOWS_APP_URL}. Переконайтеся, що він запущений і доступний.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Невідома помилка при відправленні команди '{command}' до застосунку Windows: {e}")
        return False

# --- ОБРОБНИКИ КОМАНД TELEGRAM ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        bot.reply_to(message, "Ви не авторизовані для використання цього бота.")
        return

    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = telebot.types.KeyboardButton('Запустити Тривогу 🔔')
    itembtn2 = telebot.types.KeyboardButton('Запустити Відбій 🟢')
    itembtn3 = telebot.types.KeyboardButton('Запустити Хвилину мовчання 🕯️')
    itembtn4 = telebot.types.KeyboardButton('Зупинити все 🛑')
    itembtn5 = telebot.types.KeyboardButton('Увімкнути авто Хвилину мовчання 🔄')
    itembtn6 = telebot.types.KeyboardButton('Вимкнути авто Хвилину мовчання 🚫')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)

    bot.reply_to(message, "Привіт! Я твій бот для керування звуками на Windows. Обирай дію:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Запустити Тривогу 🔔')
def handle_alarm(message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        bot.reply_to(message, "Ви не авторизовані для використання цього бота.")
        return
    if send_command_to_windows_app("play_alarm"):
        bot.reply_to(message, "Команда 'Тривога' відправлена.")
    else:
        bot.reply_to(message, "Не вдалося відправити команду 'Тривога'. Перевірте консоль для деталей.")

@bot.message_handler(func=lambda message: message.text == 'Запустити Відбій 🟢')
def handle_all_clear(message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        bot.reply_to(message, "Ви не авторизовані для використання цього бота.")
        return
    if send_command_to_windows_app("play_all_clear"):
        bot.reply_to(message, "Команда 'Відбій' відправлена.")
    else:
        bot.reply_to(message, "Не вдалося відправити команду 'Відбій'. Перевірте консоль для деталей.")

@bot.message_handler(func=lambda message: message.text == 'Запустити Хвилину мовчання 🕯️')
def handle_minute_of_silence(message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        bot.reply_to(message, "Ви не авторизовані для використання цього бота.")
        return
    if send_command_to_windows_app("play_minute_of_silence"):
        bot.reply_to(message, "Команда 'Хвилина мовчання' відправлена.")
    else:
        bot.reply_to(message, "Не вдалося відправити команду 'Хвилина мовчання'. Перевірте консоль для деталей.")

@bot.message_handler(func=lambda message: message.text == 'Зупинити все 🛑')
def handle_stop_all(message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        bot.reply_to(message, "Ви не авторизовані для використання цього бота.")
        return
    if send_command_to_windows_app("stop_all_sounds"):
        bot.reply_to(message, "Команда 'Зупинити все' відправлена.")
    else:
        bot.reply_to(message, "Не вдалося відправити команду 'Зупинити все'. Перевірте консоль для деталей.")

@bot.message_handler(func=lambda message: message.text == 'Увімкнути авто Хвилину мовчання 🔄')
def handle_enable_auto_minute_of_silence(message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        bot.reply_to(message, "Ви не авторизовані для використання цього бота.")
        return
    if send_command_to_windows_app("enable_auto_minute_of_silence"):
        bot.reply_to(message, "Автоматичну Хвилину мовчання увімкнено.")
    else:
        bot.reply_to(message, "Не вдалося увімкнути автоматичну Хвилину мовчання.")

@bot.message_handler(func=lambda message: message.text == 'Вимкнути авто Хвилину мовчання 🚫')
def handle_disable_auto_minute_of_silence(message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        bot.reply_to(message, "Ви не авторизовані для використання цього бота.")
        return
    if send_command_to_windows_app("disable_auto_minute_of_silence"):
        bot.reply_to(message, "Автоматичну Хвилину мовчання вимкнено.")
    else:
        bot.reply_to(message, "Не вдалося вимкнути автоматичну Хвилину мовчання.")

# --- ЗАПУСК БОТА ---

print("Бот запущено. Очікую команди...")
# Використовуємо poll() з обробкою помилок для підвищення стабільності
# Додаємо interval=0 для швидкого реагування
# Додаємо timeout=30 для запобігання зависанню при довгих опитуваннях
while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=30)
    except Exception as e:
        print(f"Помилка в циклі polling бота: {e}")
        # Затримка перед повторною спробою, щоб уникнути спаму запитами
        time.sleep(5)