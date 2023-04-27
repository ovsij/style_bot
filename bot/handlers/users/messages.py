from aiogram import types
from aiogram.utils import markdown
from emoji import emojize
import logging
import time
from dotenv import load_dotenv
import os

load_dotenv()

from loader import bot, dp, Form

from database.crud import *
from database.models import *
from keyboards.inline import *

text1 = markdown.text(
    emojize(':star: Аутентичный стиль начинается с понимания себя, поэтому первая часть Системы Стиля была посвящена исследованию своей индивидуальности.', language='alias'),
    emojize(':star: Задача второй части Системы — раскрыть максимальное количество граней своей внутренней уникальности через язык моды.', language='alias'),
    'Для этого мы проанализировали все существующие стили, которые составляют современную моду, с точки зрения элементов эстетики и смыслов.',
    sep = '\n\n'
)
text2 = markdown.text(
    'Каждый стиль появился как отражение определённых ценностей, стремлений и мировоззрения.', 
    emojize('Для Системы Стиля мы систематизировали все смыслы, которые несёт в себе мода, и соединили их с аспектами личной индивидуальности :sparkles:',  language='alias'),
    sep='\n\n'
)
text3 = markdown.text(
    'Ваша индивидуальность — это ваше уникальное сочетание качеств.',
    'По этому же примеру, ваш индивидуальный стиль — это уникальное сочетание элементов эстетики, отражающих вас.',
    sep='\n\n'
)
text4 = markdown.text(
    emojize(':star2: Система Стиля определила 3 ключевых стиля, которые максимально воплощают в себе ваше уникальное сочетание смыслов и качеств.',  language='alias'),
    'У вас будет возможность выбрать 2 из 3-х стилей, которые больше всех откликаются вам по эстетике и смыслам.',
    sep='\n\n'
)



@dp.message_handler(lambda message: '@' in message.text)
async def start_process(message: types.Message):
    # проверяем, обработан ли пользователь
    gc = gspread.service_account('database/credentials.json')
    gstable = gc.open_by_key(os.getenv('GS_RESULT_KEY'))
    try:
        worksheet_style = gstable.worksheet("Foglio1")
        print('Connected to "Foglio1"')
    except:
        print('Can\'t connect to "Foglio1"')

    worksheet_values = worksheet_style.get_all_values()

    if message.text.lower() not in [row[0].lower() for row in  worksheet_values]:
        await bot.send_message(message.from_user.id, text='Введенный email не найден, попробуйте еще раз.')
        return 0

    for row in worksheet_values:
        if message.text.lower() == row[0]:
            if len(row[1]) < 1:
                await bot.send_message(message.from_user.id, text=emojize('Кажется, вашу анкету еще не обработали. Попробуйте ввести свой email позже. \n\nЕсли проблема повторится - свяжитесь с нами, мы поможем ее решить :yellow_heart:', language='alias'))
                return 0
            elif row[2] == 'Активирован':
                text_and_data = [
                    ['Перейти на сайт', 'http://systemofstyle.com'],
                    ['Отправить сообщение', 'https://t.me/annamariagera']
                    ]
                schema = [1, 1]
                button_type = ['url', 'url']
                reply_markup = InlineConstructor.create_kb(text_and_data, schema, button_type)
                await bot.send_message(message.from_user.id, text='Для того, чтобы повторно воспользоваться услугой, вам необходимо заново пройти Систему Стиля.', reply_markup=reply_markup)
                return 0
            else:
                styles_list=row[1].split(', ')
                worksheet_style.update_cell(worksheet_values.index(row) + 1, 3, 'Активирован')
                logging.info(f'Пользователь {message.from_user.id}  Стили из гугл таблицы: {styles_list}')

    
    if styles_list:
        update_user(tg_id=str(message.from_user.id), styles_list=styles_list)
        styles_list = get_user_styles(message.from_user.id)
        logging.info(f'Пользователь {message.from_user.id} Стили из базы данных: {styles_list}')
        for text in [text1, text2, text3, text4]:
            await bot.send_message(message.from_user.id, text=text, reply_markup=types.ReplyKeyboardRemove())
            time.sleep(int(os.getenv('SLEEP')))
        # начало перечисления стилей
        await bot.send_message(message.from_user.id, text=emojize(f':yellow_heart: *{styles_list[0].upper()}*', language='alias'), reply_markup=types.ReplyKeyboardRemove(), parse_mode='Markdown')
        for msg in get_messages(styles_list[0]):
            await bot.send_message(message.from_user.id, text=msg.text, reply_markup=types.ReplyKeyboardRemove())
            time.sleep(int(os.getenv('SLEEP')))

            images = get_message_imgs(msg)
            media = [types.InputMedia(media=open(image.link, 'rb')) for image in images]
            await bot.send_media_group(message.from_user.id, media=media) if media else 0
            time.sleep(int(os.getenv('SLEEP')))
        
        
        text_and_data = [['Дальше', f'next_style_1']]
        schema = [1]
        inline_kb_next = InlineConstructor.create_kb(text_and_data, schema)
        button_message = await bot.send_message(message.from_user.id, text='Нажмите, чтобы продолжить', reply_markup=inline_kb_next)
        update_user(tg_id=message.from_user.id, button_message=str(button_message.message_id))
        
    else:
        await bot.send_message(message.from_user.id, text='Ваша заявка находится в стадии обработки. Как только мы закончим анализировать вашу анкету, мы пришлем вам инструкции по дальнейшим шагам!', reply_markup=types.ReplyKeyboardRemove())
    
