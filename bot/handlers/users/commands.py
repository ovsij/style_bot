import asyncio
from aiogram import types
from aiogram.utils import markdown
from dotenv import load_dotenv
import os

load_dotenv()


from loader import bot, dp

from database.crud import *
from database.models import *

@dp.message_handler(commands=['start'])
async def bot_start(message: types.Message):
    text = markdown.text(
            f'{message.from_user.first_name}, добро пожаловать!', 
            'Введите email, который вы указывали при заполнении анкеты, чтобы получить ваши результаты.',
            sep='\n')
    register_user(message.from_user)
    await bot.send_message(
        message.from_user.id,
        text=text,
    )

@dp.message_handler(commands=['update'])
async def update_database(message: types.Message):
    if str(message.from_user.id) in ['765765573', '227184505']:
        db.drop_table('Style', with_all_data=True)
        db.drop_table('Message', with_all_data=True)
        db.drop_table('MessageImage', with_all_data=True)
        db.drop_table('ElementImage', with_all_data=True)
        db.drop_table('AccentImage', with_all_data=True)
        db.drop_table('Element', with_all_data=True)
        db.create_tables()
        await bot.send_message(
            message.from_user.id,
            text='Запущен процесс обновления. Это может занять несколько минут.'
            )
        try:
            await fill_tables()
        except Exception as ex:
            print(ex)
        await bot.send_message(
            message.from_user.id,
            text='База данных успешно обновлена'
            )

@dp.message_handler(commands=['refresh'])
async def refresh_user(message: types.Message):
    if str(message.from_user.id) in ['765765573', '227184505']:
        del_user(message.from_user.id)
    