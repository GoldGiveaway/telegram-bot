import urllib.parse
import aiogram.types as types
from aiogram.utils.keyboard import InlineKeyboardMarkup, ReplyKeyboardMarkup


def giveaway_edit(giveaway_id: str, status: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            types.InlineKeyboardButton(text="Каналы 📢", callback_data=f"gedit|channel|{giveaway_id}"),
        ],
        [
            types.InlineKeyboardButton(text="Ред. название 💬", callback_data=f"gedit|title|{giveaway_id}"),
            types.InlineKeyboardButton(text="Ред. дату завершения 📅", callback_data=f"gedit|date|{giveaway_id}"),
        ],
        [
            types.InlineKeyboardButton(text="Ред. описание 📝", callback_data=f"gedit|description|{giveaway_id}"),
            types.InlineKeyboardButton(text="Ред. призовых мест 🫂", callback_data=f"gedit|win|{giveaway_id}"),
        ]
    ]

    if status == 'wait':
        buttons.append([types.InlineKeyboardButton(text="✅ Опубликовать розыгрыш ✅", callback_data=f"gedit|publish|{giveaway_id}")])
    elif status == 'active':
        buttons.append([
            types.InlineKeyboardButton(text="⌛️ Завершить розыгрыш", callback_data=f"asd"),
            types.InlineKeyboardButton(text="❌ Удалить", callback_data=f"asd")
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def giveaway_publish(link: str) -> InlineKeyboardMarkup:
    share_data = {'url': link, 'text': '\nУчаствуй в розыгрыше!'}
    buttons = [
        [types.InlineKeyboardButton(text="✅ Участвовать", url=link)],
        [types.InlineKeyboardButton(text="🔗 Поделиться",
                                    url=f'https://t.me/share/url?{urllib.parse.urlencode(share_data).replace("+", "%20")}')]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def giveaway_channel_send(giveaway_id: str, channel_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text="Отправить новое сообщение", callback_data=f'resend|{giveaway_id}|{channel_id}')],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def add_channel():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[
        types.KeyboardButton(
            text='Выбрать канал',
            request_chat=types.KeyboardButtonRequestChat(
                request_title=True,
                request_username=True,
                request_photo=True,
                request_id=1,
                chat_is_channel=True,
                user_administrator_rights=types.chat_administrator_rights.ChatAdministratorRights(
                    **{arg: False for arg in ['is_anonymous', 'can_manage_video_chats', 'can_post_stories', 'can_edit_stories', 'can_delete_stories', 'can_promote_members', 'can_change_info', 'can_manage_chat', 'can_restrict_members']},
                    can_invite_users=True,
                    can_post_messages=True,
                    can_delete_messages=True,
                    can_edit_messages=True,
                ),
                bot_administrator_rights=types.chat_administrator_rights.ChatAdministratorRights(
                    **{arg: False for arg in ['is_anonymous', 'can_manage_chat', 'can_manage_video_chats', 'can_restrict_members', 'can_promote_members', 'can_change_info', 'can_post_stories', 'can_edit_stories', 'can_delete_stories']},
                    can_invite_users=True,
                    can_post_messages=True,
                    can_delete_messages=True,
                    can_edit_messages=True,
                ),
            )
        )
    ]])
