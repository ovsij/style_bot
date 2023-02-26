from aiogram import types
from aiogram.utils import markdown
from emoji import emojize
import json
import time

from loader import bot, dp, Form

from database.crud import *
from database.models import *
from keyboards.inline import *

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

# обработчик кнопок
@dp.callback_query_handler(lambda c: c.data.startswith('next'))
async def btn_callback(callback_query: types.CallbackQuery):
    code = callback_query.data
    print(code)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=Form.button_message.message_id)
    if 'style' in code:
        styles_list = get_user_styles(callback_query.from_user.id)
        await bot.send_message(callback_query.from_user.id, text=emojize(f':yellow_heart: *{styles_list[int(code.split("_")[-1])].upper()}*', language='alias'), reply_markup=types.ReplyKeyboardRemove(), parse_mode='Markdown')
        for msg in get_messages(styles_list[int(code.split("_")[-1])]):
            await bot.send_message(callback_query.from_user.id, text=msg.text, reply_markup=types.ReplyKeyboardRemove())
            time.sleep(int(os.getenv('SLEEP')))

            images = get_message_imgs(msg)
            media = [types.InputMedia(media=open(image.link, 'rb')) for image in images]
            await bot.send_media_group(callback_query.from_user.id, media=media) if media else 0
            time.sleep(int(os.getenv('SLEEP')))
        
        if code.split('_')[-1] == '1':
            text_and_data = [['Дальше', f'next_style_2']]
            schema = [1]
            inline_kb_next = InlineConstructor.create_kb(text_and_data, schema)
            Form.button_message = await bot.send_message(callback_query.from_user.id, text='Нажмите, чтобы продолжить', reply_markup=inline_kb_next)
        else:
            for text in [text5, text6]:
                await bot.send_message(callback_query.from_user.id, text=text)
                time.sleep(int(os.getenv('SLEEP')))
            Form.form_message = await bot.send_poll(chat_id=callback_query.from_user.id, question='Выберите два из предложенных стилей',
									is_anonymous=False, options=list(styles_list), allows_multiple_answers=True)
        
    if 'base' in code:
        text = markdown.text(
            emojize(':star: Помимо акцентов вы можете использовать базовые вещи для дополнения образов на каждый день.', language='alias'),
            emojize(':point_right: Старайтесь выбирать базу, которая максимально соответствует вашей формуле стиля.', language='alias'),
            sep='\n\n')
        await bot.send_message(callback_query.from_user.id, text=text)
        time.sleep(int(os.getenv('SLEEP'))/2)

        for style in get_user_styles(tg_id=callback_query.from_user.id):
            text = emojize(f':yellow_heart: *Примеры базы для стиля {style}:*\n', language='alias')
            text += get_style_base(style) + '\n\n'
            await bot.send_message(callback_query.from_user.id, text=text, parse_mode="Markdown")
            time.sleep(int(os.getenv('SLEEP')))

        text_and_data = [['Дальше', f'next_final_1']]
        schema = [1]
        inline_kb_next = InlineConstructor.create_kb(text_and_data, schema)
        Form.button_message = await bot.send_message(callback_query.from_user.id, text='Нажмите, чтобы продолжить', reply_markup=inline_kb_next)

    if 'final' in code:
        text = markdown.text(
            emojize(':star: Как воплотить свой аутентичный стиль:', language='alias'),
            '*1. Собирайте образы вокруг своей формулы стиля, используя ее как чек-лист:\n*',
            sep='\n\n')
        for style in get_user_styles(tg_id=callback_query.from_user.id):
            for element in get_user_elements_by_style(tg_id=callback_query.from_user.id, style=style):
                text += f'• {element.name}\n'
        text += emojize('\n:point_right: В образе должно быть что-то из каждого элемента. Одна вещь может воплощать в себе сразу несколько элементов. Например, блуза может быть одновременно нежной и расслабленной, или яркой и нарядной.', language='alias')
        text += emojize('\n\n:point_right: Не бойтесь сочетать между собой противоположные элементы в вашей формуле стиля, именно контрасты создают яркий индивидуальный стиль. Например, если у вас есть элементы «женственность» и «мужская классика», вы можете надеть пиджак, сделав акцент с помощью пояса на талии.', language='alias')
        await bot.send_message(callback_query.from_user.id, text=text, parse_mode="Markdown")
        time.sleep(int(os.getenv('SLEEP')))

        text = '*2. Дополняйте образ базовыми вещами, которые подходят к вашему стилю.*'
        await bot.send_message(callback_query.from_user.id, text=text, parse_mode="Markdown")
        time.sleep(int(os.getenv('SLEEP'))/2)

        text = '*3. Для того чтобы легко собирать образы, переберите свой гардероб и посмотрите, что из того, что у вас есть, соответствует акцентам и базе вашего стиля.\n\n*'
        text += emojize('Если вы сомневаетесь в чем-то, слушайте себя, индивидуальный стиль — это про ваше видение. Опирайтесь на свою формулу стиля и не бойтесь пробовать и экспериментировать :sparkles:', language='alias')
        await bot.send_message(callback_query.from_user.id, text=text, parse_mode="Markdown")
        time.sleep(int(os.getenv('SLEEP')))

        text = markdown.text(
            '*4. Когда вы разберёте свой гардероб, вы поймёте, каких элементов вашей формулы стиля и какой базы вам не хватает.*',
            emojize(':point_right: Составьте список недостающих вещей для создания образов. Не обязательно покупать все сразу, можно периодически пополнять свой гардероб одной, двумя вещами.', language='alias'),
            emojize(':point_right: Самый простой способ создавать свой стиль — использовать акцентные аксессуары, которые могут сделать даже базовый образ индивидуальным.', language='alias'),
            sep='\n\n')
        await bot.send_message(callback_query.from_user.id, text=text, parse_mode="Markdown")
        time.sleep(int(os.getenv('SLEEP')))

        text = markdown.text(
            '*5. Система Аутентичного Стиля — это структура, которую вы можете наполнять тем, что максимально про вас.*', 
            emojize('Пробуйте разные элементы своего индивидуального стиля, потребуется какое-то время, чтобы реализовать свой стиль в своем гардеробе. Опираясь на знания о своей индивидуальности и о том, как проявить ее вовне, можно делать целенаправленную работу, которая с каждым днём будет все больше приближать вас к вашему уникальному и узнаваемому стилю. :heart:', language='alias'),
            sep='\n\n')
        await bot.send_message(callback_query.from_user.id, text=text, parse_mode="Markdown")