from aiogram import types
from aiogram.utils import markdown
from emoji import emojize
import time
from dotenv import load_dotenv
import os

load_dotenv()

from database.crud import *
from keyboards.inline import *
from loader import bot, dp, Form

@dp.poll_answer_handler(lambda message: 'Выберите два из предложенных стилей' in Form.form_message.poll.question)
async def handle_poll_answer(poll_answer: types.PollAnswer):
    styles_list = [style['text'] for style in Form.form_message.poll.options]
    if len(poll_answer.option_ids) == 2:
        try:
            await bot.delete_message(chat_id=poll_answer.user.id, message_id=Form.form_message.message_id)
        except:
            pass
        update_user(tg_id=poll_answer.user.id, styles_list=[styles_list[i] for i in poll_answer.option_ids])
        logging.info(f'Пользователь {poll_answer.user.id} Выбранные стили: {[styles_list[i] for i in poll_answer.option_ids]}')
        styles_list = get_user_styles(poll_answer.user.id)
        logging.info(f'Пользователь {poll_answer.user.id} Стили из бд: {styles_list}')
        await bot.send_message(poll_answer.user.id, text=emojize(':star: Каждый стиль создаётся с помощью своего набора узнаваемых элементов эстетики.', language='alias'))
        time.sleep(int(os.getenv('SLEEP')))
        for style in styles_list:
            text = f'*Элементы стиля {style}:\n*'
            for element in get_styles_elements(style):
                text += f'• {element.name} {element.description}\n'
            images = get_element_image(style)
            media = [types.InputMedia(media=open(image, 'rb')) for image in images]
            await bot.send_message(poll_answer.user.id, text=text, parse_mode="Markdown")
            time.sleep(int(os.getenv('SLEEP')))
            await bot.send_media_group(chat_id=poll_answer.user.id, media=media)
            time.sleep(int(os.getenv('SLEEP')))
        text = 'Посмотрите на элементы эстетики ваших ключевых стилей — есть ли среди них что-то, что совсем вам не подходит? Выберите те элементы, которые вы хотите использовать в своих образах (от 3 до 7). Скоро у вас будут конкретные списки предметов гардероба и примеры для того, чтобы воплотить эти элементы в своем стиле.'
        await bot.send_message(poll_answer.user.id, text=text)
        time.sleep(int(os.getenv('SLEEP')))
        forms = []
        for style in styles_list:
            element_list = []
            for element in get_styles_elements(style):
                element_list.append(element.name)
            msg = await bot.send_poll(chat_id=poll_answer.user.id, question=f'Выберите элементы стиля «{style}» (можно оставить все)',
									is_anonymous=False, options=element_list, allows_multiple_answers=True)
            forms.append(msg)
        Form.form_message = forms[0]
        Form.form_message1 = forms[1]
    elif len(poll_answer.option_ids) == 0:
        pass
    else:
        await bot.send_message(poll_answer.user.id, text='Пожалуйста, выберите ДВА стиля. Зажмите сообщение с опросом и выберите "отменить голос", чтобы направить новый ответ.')


@dp.poll_answer_handler(lambda message: 'Выберите элементы стиля' in Form.form_message.poll.question)
async def handle_poll_answer(poll_answer: types.PollAnswer):
    if poll_answer.poll_id == Form.form_message.poll.id:
        elements_list = get_styles_elements(Form.form_message.poll.question.split('«')[1].split('»')[0])
        print('1')
        print(Form.form_message.poll)
        print(elements_list)
        logging.info(f'Пользователь {poll_answer.user.id} Элементы 1 опрос: {elements_list}')
        try:
            await bot.delete_message(chat_id=poll_answer.user.id, message_id=Form.form_message.message_id)
        except:
            pass
    if poll_answer.poll_id == Form.form_message1.poll.id:
        elements_list = get_styles_elements(Form.form_message1.poll.question.split('«')[1].split('»')[0])
        print('2')
        print(Form.form_message1.poll)
        print(elements_list)
        logging.info(f'Пользователь {poll_answer.user.id} Элементы 2 опрос: {elements_list}')
        try:
            await bot.delete_message(chat_id=poll_answer.user.id, message_id=Form.form_message1.message_id)
        except:
            pass
    update_user(tg_id=poll_answer.user.id, elements_list=[elements_list[i] for i in poll_answer.option_ids])
    if check_elements(tg_id=poll_answer.user.id):
        text = 'Набор элементов эстетики ваших ключевых стилей — это ваша формула стиля. Вы можете использовать формулу как чек-лист при создании образов.'
        await bot.send_message(poll_answer.user.id, text=text)
        time.sleep(int(os.getenv('SLEEP')))

        text = emojize(':star: Предметы одежды и аксессуаров, которые создают формулу стиля, называются акцентами, потому что они ответствены за индивидуальность и узнаваемость образа.', language='alias')
        await bot.send_message(poll_answer.user.id, text=text)
        time.sleep(int(os.getenv('SLEEP')))
        
        styles_list = get_user_styles(tg_id=poll_answer.user.id)
        text = f'*{styles_list[0].upper()}\n\n*'
        for element in get_user_elements_by_style(poll_answer.user.id, styles_list[0]):
            text += emojize(f':yellow_heart: *{element.name}*\n', language='alias')
            text += element.accents + '\n\n'
        await bot.send_message(poll_answer.user.id, text=text, parse_mode="Markdown")
        time.sleep(int(os.getenv('SLEEP')))
        images = get_accents_images(styles_list[0])
        media = [types.InputMedia(media=open(image, 'rb')) for image in images]
        await bot.send_media_group(poll_answer.user.id, media=media) if media else 0
        time.sleep(int(os.getenv('SLEEP')))

        # далее
        text_and_data = [['Дальше', f'next_element_1']]
        schema = [1]
        inline_kb_next = InlineConstructor.create_kb(text_and_data, schema)
        Form.button_message = await bot.send_message(poll_answer.user.id, text='Нажмите, чтобы продолжить', reply_markup=inline_kb_next)


