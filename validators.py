import logging  # модуль для сбора логов
import math  # математический модуль для округления
# подтягиваем константы из config файла
import sqlite3
from config import LOGS, MAX_USERS, MAX_USER_GPT_TOKENS, DB_FILE, MAX_USER_TTS_SYMBOLS, MAX_USER_STT_BLOCKS
# подтягиваем функции для работы с БД
from database import count_users, count_all_limits 
# подтягиваем функцию для подсчета токенов в списке сообщений
from yandex_gpt import count_gpt_tokens
from creds import get_bot_token
import telebot
bot = telebot.TeleBot(get_bot_token())
# настраиваем запись логов в файл
logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")
path_to_db = DB_FILE
# получаем количество уникальных пользователей, кроме самого пользователя
def check_number_of_users(user_id):
    count = count_users(user_id)
    if count is None:
        return None, "Ошибка при работе с БД"
    if count > MAX_USERS:
        return None, "Превышено максимальное количество пользователей"
    return True, ""

# проверяем, не превысил ли пользователь лимиты на общение с GPT
def is_gpt_token_limit(messages, total_spent_tokens):
    all_tokens = count_gpt_tokens(messages) + total_spent_tokens
    if all_tokens > MAX_USER_GPT_TOKENS:
        return None, f"Превышен общий лимит GPT-токенов {MAX_USER_GPT_TOKENS}"
    return all_tokens, ""

# проверяем, не превысил ли пользователь лимиты на преобразование аудио в текст
def is_stt_block_limit(user_id, duration):      
     # Переводим секунды в аудиоблоки
    audio_blocks = math.ceil(duration / 15) # округляем в большую сторону
    all_blocks =  count_all_limits(user_id, "stt_blocks") + audio_blocks
    if duration >= 30:
        msg = "SpeechKit STT работает с голосовыми сообщениями меньше 30 секунд"
        bot.send_message(user_id, msg)
        return None
    if all_blocks >= MAX_USER_STT_BLOCKS:
        msg = f"Превышен общий лимит SpeechKit STT {MAX_USER_STT_BLOCKS}. Использовано {all_blocks} блоков. Доступно: {MAX_USER_STT_BLOCKS - all_blocks}"
        bot.send_message(user_id, msg)
        return None
    return audio_blocks 

# проверяем, не превысил ли пользователь лимиты на преобразование текста в аудио
def is_tts_symbol_limit(user_id, text):
    text_symbols = len(text)
    all_symbols = count_all_limits(user_id) + text_symbols
    # Сравниваем all_symbols с количеством доступных пользователю символов
    if all_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = f"Превышен общий лимит SpeechKit TTS {MAX_USER_TTS_SYMBOLS}. Использовано: {all_symbols} символов. Доступно: {MAX_USER_TTS_SYMBOLS - all_symbols}"
        bot.send_message(user_id, msg)
        return None
    # Сравниваем количество символов в тексте с максимальным количеством символов в тексте
    if text_symbols >= MAX_USER_TTS_SYMBOLS: 
        msg = f"Превышен лимит SpeechKit TTS на запрос {MAX_USER_TTS_SYMBOLS}, в сообщении {text_symbols} символов"
        bot.send_message(user_id, msg)
        return None
    return len(text) 


def execute_selection_query(sql_query, data=None, db_path=DB_FILE):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    if data:
        cursor.execute(sql_query, data)
    else:
        cursor.execute(sql_query)
    rows = cursor.fetchall()
    connection.close()
    return rows
     