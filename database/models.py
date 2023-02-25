from datetime import datetime
from decimal import Decimal
from pony.orm import *

db = Database()


class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    tg_id = Required(Decimal, unique=True)
    username = Optional(str, unique=True)
    first_name = Optional(str, nullable=True)
    last_name = Optional(str, nullable=True)
    was_registered = Optional(datetime, default=lambda: datetime.now())
    styles = Set('Style')
    elements = Set('Element')


class Style(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    messages = Set('Message')
    elements = Set('Element')
    base = Optional(str)
    element_images = Set('ElementImage')
    accent_images = Set('AccentImage')
    users = Set(User)

class Message(db.Entity):
    id = PrimaryKey(int, auto=True)
    style = Required(Style)
    text = Optional(str)
    images = Set('MessageImage')

class MessageImage(db.Entity):
    id = PrimaryKey(int, auto=True)
    message = Optional(Message)
    link = Optional(str)

class ElementImage(db.Entity):
    id = PrimaryKey(int, auto=True)
    style = Optional(Style)
    link = Optional(str)

class AccentImage(db.Entity):
    id = PrimaryKey(int, auto=True)
    style = Optional(Style)
    link = Optional(str)

class Element(db.Entity):
    id = PrimaryKey(int, auto=True)
    style = Required(Style)
    name = Optional(str)
    description = Optional(str)
    accents = Optional(str)
    users = Set(User)


    