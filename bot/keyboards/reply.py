from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import markdown


def reply_kb_start(telegram_user):
    text = markdown.text(
        f'{telegram_user.first_name}, добро пожаловать!', 
        'Нажмите кнопку ниже, чтобы поделиться с нами номером телефона и получить информацию о стилях',
        sep='\n')

    reply_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    reply_kb.add(KeyboardButton('Поделиться номером телефона', request_contact=True))
    return text, reply_kb