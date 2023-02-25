import asyncio
import gspread
from dotenv import load_dotenv
import os

load_dotenv()

from .db import *
from .yd import *

@db_session
def register_user(telegram_user):
    if not User.exists(tg_id = telegram_user.id):
        user = User(
            tg_id=telegram_user.id, 
            username=telegram_user.username, 
            first_name=telegram_user.first_name, 
            last_name=telegram_user.last_name)
        flush()
        return user
    else:
        print(f'User {telegram_user.id} exists')

@db_session
def get_user(telegram_user):
    return User.get(tg_id=telegram_user.id)

@db_session
def get_users():
    return User.select(int(u.tg_id) for u in User)

@db_session
def get_style(name : str):
    return Style.get(name=name)

@db_session
def get_element(name : str):
    return Element.get(name=name)

@db_session
def get_messages(style_name : str):
    style = Style.get(name=style_name)
    return select(m for m in Message if m.style == style)[:]

@db_session
def get_message_imgs(message : Message):
    return select(i for i in MessageImage if i.message == message)[:]

@db_session
def get_user_styles(tg_id : str):
    user = User.get(tg_id=tg_id)
    return select(s.name for s in Style if user in s.users)[:]

@db_session
def get_styles_elements(style : str):
    return select(el for el in Element if el.style == Style.get(name=style))[:]

@db_session
def get_style_base(style : str):
    return Style.get(name=style).base

@db_session
def get_user_elements(tg_id : str):
    return select(el for el in Element if User.get(tg_id=tg_id) in el.users)[:]

@db_session
def get_user_elements_by_style(tg_id : str, style : Style):
    return select(el for el in Element if User.get(tg_id=tg_id) in el.users and el.style == Style.get(name=style))[:]

@db_session
def get_element_image(style):
    return select(img.link for img in ElementImage if img.style == Style.get(name=style))[:]

@db_session
def get_accents_images(style):
    return select(img.link for img in AccentImage if img.style == Style.get(name=style))[:]

@db_session
def check_elements(tg_id):
    user = User.get(tg_id=tg_id)
    elements = select(el for el in Element if user in el.users)[:]
    styles = set([el.style for el in elements])
    return bool(len(styles) == 2)
        
@db_session
def update_user(
    tg_id : int, 
    username : str = None,
    first_name : str = None,
    last_name : str = None,
    styles_list : list = None,
    elements_list : list = None
    ):

    user_to_update = User.get(tg_id = tg_id)
    if username:
        user_to_update.username = username
    if first_name:
        user_to_update.first_name = first_name
    if last_name:
        user_to_update.last_name = last_name
    if styles_list:
        user_to_update.styles = [get_style(name) for name in styles_list]
    if elements_list:
        user_to_update.elements += [Element[el.id] for el in elements_list]




@db_session
async def fill_tables():
    # Записываем таблицу Style
    gc = gspread.service_account('database/credentials.json')
    gstable = gc.open_by_key(os.getenv('GS_KEY'))
    worksheet_style = gstable.worksheet("Стиль")
    
    tasks = []
    for style in worksheet_style.get_all_values()[1:]:
        # Заполняем таблицу Style
        style_obj = Style(name=style[0], base=style[1])
        commit()
        # Записываем изображения к элементам стиля

        counter = 1
        
        for image in style[2].strip().split('\n'):
            # запись в бд
            path=f'database/image/{style[0]}_element_{counter}.jpeg'
            ElementImage(style=style_obj, link=path)
            commit()
            tasks.append(asyncio.create_task(download_image(url=image, path=path))) if not os.path.exists(path) else 0
            counter +=1
        # Записываем изображения к акцентам
        counter = 1
        for image in style[3].strip().split('\n'):
            # запсь в бд
            path = f'database/image/{style[0]}_accent_{counter}.jpeg'
            AccentImage(style=style_obj, link=path)
            commit()
            tasks.append(asyncio.create_task(download_image(url=image, path=path))) if not os.path.exists(path) else 0
            counter +=1
        
    # Заполняем таблицу Message
    worksheet_message = gstable.worksheet("Сообщения с описанием стилей")
    for message in worksheet_message.get_all_values()[1:]:
        message_obj = Message(style=Style.get(name=message[0]), text=message[1])
        commit()
        images = message[2].strip().split('\n')
        if len(images[0]) > 0:
            counter = 1
            for image in message[2].strip().split('\n'):
                path = f'database/image/{message[0]}_message_{message_obj.id}_{counter}.jpeg'
                MessageImage(message=message_obj, link=path)  
                commit()
                tasks.append(asyncio.create_task(download_image(url=image, path=path))) if not os.path.exists(path) else 0
                counter += 1
        else:
            continue
    # Заполняем таблицу Element
    worksheet_elements = gstable.worksheet("Элементы эстетики")
    for element in worksheet_elements.get_all_values()[1:]:
        Element(style=Style.get(name=element[3]), name=element[0], description=element[1], accents=element[2])

    return await asyncio.gather(*tasks)
    