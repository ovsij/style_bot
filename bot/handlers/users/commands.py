import asyncio
from aiogram import types
from aiogram.utils import markdown
from dotenv import load_dotenv
import os

load_dotenv()


from loader import bot, dp, Form

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
            logging.warning(ex)
        await bot.send_message(
            message.from_user.id,
            text='База данных успешно обновлена'
            )

@dp.message_handler(commands=['refresh'])
async def refresh_user(message: types.Message):
    del_user(message.from_user.id)
    await bot.send_message(
            message.from_user.id,
            text='Ваши данные обновлены. Введите команду /start, чтобы начать заново.'
            )
    

@dp.message_handler(commands=['f'])
async def refresh_user(message: types.Message):
    print(Form.form_message)

@dp.message_handler(commands=['fu'])
async def refresh_user(message: types.Message):
    print(Form.form_message[message.from_user.id])
    