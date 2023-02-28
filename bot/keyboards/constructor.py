from typing import Dict, List, Tuple, Union

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class InlineConstructor:

    @staticmethod
    def create_kb(
        text_and_data: list,
        schema: list,
        button_type: list = None
    ) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup()
        kb.row_width = max(schema)
        btns = []
        if not button_type:
            button_type = []
            for i in range(len(text_and_data)):
                button_type.append('callback_data')

        if sum(schema) == len(text_and_data):
            for i in range(len(schema)):
                if button_type[i] == 'callback_data':
                    row_btns = (InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data[:schema[i]])
                    kb.row(*row_btns)
                elif button_type[i] == 'url':
                    row_btns = (InlineKeyboardButton(text, url=data) for text, data in text_and_data[:schema[i]])
                    kb.row(*row_btns)
                
                for _ in range(schema[i]):
                    text_and_data.pop(0)
        else:
            print('Number of buttons does not match the schema')
            
        return kb