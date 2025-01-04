import aiogram.types as types
from aiogram.utils.keyboard import InlineKeyboardMarkup


def menu() -> InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text="Мои розыгрыши 📋", callback_data="asd")],
        [types.InlineKeyboardButton(text="Создать розыгрыш ➕", callback_data="giveaway|create")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def go_home() -> InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text="◀️ В меню", callback_data="menu")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
