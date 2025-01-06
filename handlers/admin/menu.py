from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from services import db

router = Router(name=__name__)


@router.message(Command("admin"))
async def _(message: Message):
    await message.answer(
        f'🫂 Пользователей: <b>{await db.users_collection.count_documents({})}</b>\n\n'
        f'🎁 Розыгрышей:\n'
        f'| Созданных: <b>{await db.giveaways_collection.count_documents({"status": "wait"})}</b>\n'
        f'| Активных: <b>{await db.giveaways_collection.count_documents({"status": "active"})}</b>\n'
        f'| Прошедших: <b>{await db.giveaways_collection.count_documents({"status": "finalized"})}</b>'
    )
