from aiogram import types
from aiogram.utils import markdown
from emoji import emojize
import time
from dotenv import load_dotenv
import os

load_dotenv()

from loader import bot, dp, Form

from database.crud import *
from database.models import *
from keyboards.inline import *
from keyboards.reply import *

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
text5 = markdown.text(
    emojize(':point_right: Индивидуальный стиль состоит из сочетания элементов эстетики 2-х стилей, максимально отражающих вашу индивидуальность.', language='alias'),
    'Выберите для себя 2 из 3-х стилей, которые больше всего откликаются вам по смыслам и эстетике. Пока не думайте о том, как именно воплотить стили в своем гардеробе, скоро у вас будут конкретные рекомендации и примеры.',
    sep = '\n\n'
)
text6 = markdown.text(
    emojize('На заметку :heart:', language = 'alias'),
    'Качества и смыслы, которые составляют вашу индивидуальность, значимы не только в сфере стиля, но и во всех аспектах жизни, где вам важно осознавать и проявлять свою уникальность, например, в вашей деятельности. Чем больше вы следуете себе и чувствуете соответствие между внутренним и внешним, тем больше вы проявляете свою индивидуальную ценность в мир.',
    sep = '\n\n'
)


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def change_phone(message: types.Message):
    # проверяем, обработан ли пользователь
    styles_list = ['Бохо', '60-е', 'Сафари']
    #styles_list = []
    if styles_list:
        update_user(tg_id=str(message.from_user.id), styles_list=styles_list)
        for text in [text1, text2, text3, text4]:
            await bot.send_message(message.from_user.id, text=text, reply_markup=types.ReplyKeyboardRemove())
            time.sleep(int(os.getenv('SLEEP')))
        for style in styles_list:
            await bot.send_message(message.from_user.id, text=emojize(f':yellow_heart: *{style.upper()}*', language='alias'), reply_markup=types.ReplyKeyboardRemove(), parse_mode='Markdown')
            for msg in get_messages(style):
                await bot.send_message(message.from_user.id, text=msg.text, reply_markup=types.ReplyKeyboardRemove())
                time.sleep(int(os.getenv('SLEEP')))
                images = get_message_imgs(msg)
                media = [types.InputMedia(media=open(image.link, 'rb')) for image in images]
                await bot.send_media_group(message.from_user.id, media=media) if media else 0
                time.sleep(int(os.getenv('SLEEP')))
        for text in [text5, text6]:
            await bot.send_message(message.from_user.id, text=text)
            time.sleep(int(os.getenv('SLEEP')))
        Form.form_message = await bot.send_poll(chat_id=message.from_user.id, question='Выберите два из предложенных стилей',
									is_anonymous=False, options=styles_list, allows_multiple_answers=True)
    else:
        await bot.send_message(message.from_user.id, text='Ваша заявка находится в стадии обработки. Как только мы закончим анализировать вашу анкету, мы пришлем вам инструкции по дальнейшим шагам!', reply_markup=types.ReplyKeyboardRemove())
    
