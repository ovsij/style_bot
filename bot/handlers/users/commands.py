import asyncio
from aiogram import types


from loader import bot, dp
from bot.keyboards.reply import reply_kb_start

from database.crud import *
from database.models import *

@dp.message_handler(commands=['start'])
async def bot_start(message: types.Message):
    if register_user(message.from_user):
        text, reply_markup = reply_kb_start(message.from_user)

        await bot.send_message(
            message.from_user.id,
            text=text,
            reply_markup=reply_markup
        )
    else:
        # заменить на pass
        text, reply_markup = reply_kb_start(message.from_user)
        await bot.send_message(
            message.from_user.id,
            text=text,
            reply_markup=reply_markup
        )

@dp.message_handler(commands=['update'])
async def update_database(message: types.Message):
    db.drop_all_tables(with_all_data=True)
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