from aiogram import types
from aiogram.utils import markdown
from emoji import emojize
import time
from dotenv import load_dotenv
import os

load_dotenv()

from database.crud import *
from loader import bot, dp, Form

@dp.poll_answer_handler(lambda message: 'Выберите два из предложенных стилей' in Form.form_message.poll.question)
async def handle_poll_answer(poll_answer: types.PollAnswer):
    styles_list = [style['text'] for style in Form.form_message.poll.options]
    if len(poll_answer.option_ids) == 2:
        await bot.delete_message(chat_id=poll_answer.user.id, message_id=Form.form_message.message_id)
        update_user(tg_id=poll_answer.user.id, styles_list=[styles_list[i] for i in poll_answer.option_ids])
        styles_list = get_user_styles(poll_answer.user.id)
        await bot.send_message(poll_answer.user.id, text=emojize(':star: Каждый стиль создаётся с помощью своего набора узнаваемых элементов эстетики', language='alias'))
        time.sleep(int(os.getenv('SLEEP'))/2)
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
        text = 'Посмотрите на элементы эстетики ваших ключевых стилей — есть ли среди них что-то, что совсем вам не подходит? Выберите те элементы, которые вы хотите использовать в своих образах (от 4 до 7). Скоро у вас будут конкретные списки предметов гардероба и примеры для того, чтобы воплотить эти элементы в своем стиле.'
        await bot.send_message(poll_answer.user.id, text=text)
        time.sleep(int(os.getenv('SLEEP')))
        forms = []
        for style in styles_list:
            element_list = []
            for element in get_styles_elements(style):
                element_list.append(element.name)
            msg = await bot.send_poll(chat_id=poll_answer.user.id, question=f'Выберите элементы стиля {style} (можно оставить все)',
									is_anonymous=False, options=element_list, allows_multiple_answers=True)
            forms.append(msg)
        Form.form_message = forms[0]
        Form.form_message1 = forms[1]
    elif len(poll_answer.option_ids) == 0:
        pass
    else:
        await bot.send_message(poll_answer.user.id, text='Пожалуйста, выберите ДВА стиля. Зажмите сообщение с опросом и выберите "отменить голос", чтобы пепеголосовать.')


@dp.poll_answer_handler(lambda message: 'Выберите элементы стиля' in Form.form_message.poll.question)
async def handle_poll_answer(poll_answer: types.PollAnswer):
    if poll_answer.poll_id == Form.form_message.poll.id:
        elements_list = get_styles_elements(Form.form_message.poll.question.split(' (')[0].split(' ')[-1])
        await bot.delete_message(chat_id=poll_answer.user.id, message_id=Form.form_message.message_id)
    if poll_answer.poll_id == Form.form_message1.poll.id:
        elements_list = get_styles_elements(Form.form_message1.poll.question.split(' (')[0].split(' ')[-1])
        await bot.delete_message(chat_id=poll_answer.user.id, message_id=Form.form_message1.message_id)
    update_user(tg_id=poll_answer.user.id, elements_list=[elements_list[i] for i in poll_answer.option_ids])
    if check_elements(tg_id=poll_answer.user.id):
        text = 'Набор элементов эстетики ваших ключевых стилей — это ваша формула стиля. Вы можете использовать формулу как чек-лист при создании образов.'
        await bot.send_message(poll_answer.user.id, text=text)
        time.sleep(int(os.getenv('SLEEP'))/2)

        text = emojize(':star: Предметы одежды и аксессуаров, которые создают формулу стиля, называются акцентами, потому что они ответствены за индивидуальность и узнаваемость образа.', language='alias')
        await bot.send_message(poll_answer.user.id, text=text)
        time.sleep(int(os.getenv('SLEEP'))/2)
        
        for style in get_user_styles(tg_id=poll_answer.user.id):
            text = f'*{style.upper()}\n\n*'
            for element in get_user_elements_by_style(poll_answer.user.id, style):
                text += emojize(f':yellow_heart: *{element.name}*\n', language='alias')
                text += element.accents + '\n\n'
            await bot.send_message(poll_answer.user.id, text=text, parse_mode="Markdown")
            images = get_accents_images(style)
            media = [types.InputMedia(media=open(image, 'rb')) for image in images]
            await bot.send_media_group(poll_answer.user.id, media=media) if media else 0
            time.sleep(int(os.getenv('SLEEP')))
        
        text = emojize(':point_right: Для создания образов в вашем стиле достаточно 1-го пункта из каждого элемента формулы стиля. На практике это несложно — 1 вещь или 1 аксессуар могут воплотить в себе сразу несколько пунктов.', language='alias')
        await bot.send_message(poll_answer.user.id, text=text)
        time.sleep(int(os.getenv('SLEEP'))/2)

        text = markdown.text(
            emojize(':point_right: Если среди ваших акцентов есть противоречащие друг другу пункты, например яркие и пастельные цвета, это значит, что вам подходят оба варианта.', language='alias'),
            'Цель — не использовать все свои акценты в образе, а постараться отразить каждый элемент своей формулы стиля.',
            emojize('Именно уникальное сочетание элементов эстетики вашей формулы стиля будет создавать ваш аутентичный, узнаваемый стиль :sparkles:', language='alias'),
            sep='\n\n'
            )
        await bot.send_message(poll_answer.user.id, text=text)
        time.sleep(int(os.getenv('SLEEP')))

        text = markdown.text(
            emojize(':star: Помимо акцентов вы можете использовать базовые вещи для дополнения образов на каждый день.', language='alias'),
            emojize(':point_right: Старайтесь выбирать базу, которая максимально соответствует вашей формуле стиля.', language='alias'),
            sep='\n\n')
        await bot.send_message(poll_answer.user.id, text=text)
        time.sleep(int(os.getenv('SLEEP'))/2)

        for style in get_user_styles(tg_id=poll_answer.user.id):
            text = emojize(f':yellow_heart: *Примеры базы для стиля {style}:*\n', language='alias')
            text += get_style_base(style) + '\n\n'
            await bot.send_message(poll_answer.user.id, text=text, parse_mode="Markdown")
            time.sleep(int(os.getenv('SLEEP')))

        text = markdown.text(
            emojize(':star: Как воплотить свой аутентичный стиль:', language='alias'),
            '*1. Собирайте образы вокруг своей формулы стиля, используя ее как чек-лист:\n*',
            sep='\n\n')
        for style in get_user_styles(tg_id=poll_answer.user.id):
            for element in get_user_elements_by_style(tg_id=poll_answer.user.id, style=style):
                text += f'• {element.name}\n'
        text += emojize('\n:point_right: В образе должно быть что-то из каждого элемента. Одна вещь может воплощать в себе сразу несколько элементов. Например, блуза может быть одновременно нежной и расслабленной, или яркой и нарядной.', language='alias')
        text += emojize('\n\n:point_right: Не бойтесь сочетать между собой противоположные элементы в вашей формуле стиля, именно контрасты создают яркий индивидуальный стиль. Например, если у вас есть элементы «женственность» и «мужская классика», вы можете надеть пиджак, сделав акцент с помощью пояса на талии.', language='alias')
        await bot.send_message(poll_answer.user.id, text=text, parse_mode="Markdown")
        time.sleep(int(os.getenv('SLEEP')))

        text = '*2. Дополняйте образ базовыми вещами, которые подходят к вашему стилю.*'
        await bot.send_message(poll_answer.user.id, text=text, parse_mode="Markdown")
        time.sleep(int(os.getenv('SLEEP'))/2)

        text = '*3. Для того чтобы легко собирать образы, переберите свой гардероб и посмотрите, что из того, что у вас есть, соответствует акцентам и базе вашего стиля.\n\n*'
        text += emojize('Если вы сомневаетесь в чем-то, слушайте себя, индивидуальный стиль — это про ваше видение. Опирайтесь на свою формулу стиля и не бойтесь пробовать и экспериментировать :sparkles:', language='alias')
        await bot.send_message(poll_answer.user.id, text=text, parse_mode="Markdown")
        time.sleep(int(os.getenv('SLEEP')))

        text = markdown.text(
            '*4. Когда вы разберёте свой гардероб, вы поймёте, каких элементов вашей формулы стиля и какой базы вам не хватает.*',
            emojize(':point_right: Составьте список недостающих вещей для создания образов. Не обязательно покупать все сразу, можно периодически пополнять свой гардероб одной, двумя вещами.', language='alias'),
            emojize(':point_right: Самый простой способ создавать свой стиль — использовать акцентные аксессуары, которые могут сделать даже базовый образ индивидуальным.', language='alias'),
            sep='\n\n')
        await bot.send_message(poll_answer.user.id, text=text, parse_mode="Markdown")
        time.sleep(int(os.getenv('SLEEP')))

        text = markdown.text(
            '*5. Система Аутентичного Стиля — это структура, которую вы можете наполнять тем, что максимально про вас.*', 
            emojize('Пробуйте разные элементы своего индивидуального стиля, потребуется какое-то время, чтобы реализовать свой стиль в своем гардеробе. Опираясь на знания о своей индивидуальности и о том, как проявить ее вовне, можно делать целенаправленную работу, которая с каждым днём будет все больше приближать вас к вашему уникальному и узнаваемому стилю. :heart:', language='alias'),
            sep='\n\n')
        await bot.send_message(poll_answer.user.id, text=text, parse_mode="Markdown")

