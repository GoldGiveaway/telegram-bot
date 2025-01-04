import aiogram.types as types
from aiogram.utils.keyboard import InlineKeyboardMarkup


def menu() -> InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text="Мои розыгрыши 📋", callback_data="giveaway|list")],
        [types.InlineKeyboardButton(text="Создать розыгрыш ➕", callback_data="giveaway|create")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def go_home() -> InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text="◀️ В меню", callback_data="menu")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def giveaway_list(giveaways: list[dict]) -> InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text=giveaway['title'], callback_data=f"giveaway|edit|{giveaway['giveaway_id']}")]
        for giveaway in giveaways
    ]

    buttons += [types.InlineKeyboardButton(text="◀️ В меню", callback_data="menu")],

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def clear_keyboard():
    return types.ReplyKeyboardRemove()
