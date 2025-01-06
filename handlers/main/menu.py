from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards import for_index
from services import db

router = Router(name=__name__)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Command: /start"""

    await state.clear()
    await message.answer_photo(
        photo='https://i.imgur.com/FRYuxCD.png',
        caption='<b>👋 Добро пожаловать! Я помогу провести розыгрыш для твоей аудитории!</b>\n\n'
                'Я могу создать розыгрыш между одним или несколько каналов/чатов, а ещё автоматически определить победителя\n\n'
                '<a href="https://gold-giveaway.ru/">🌳 Сайт</a>\n'
                '<a href="https://t.me/isSteam">🌳 Telegram канал разработчика</a>\n',
        reply_markup=for_index.menu()
    )


@router.callback_query(F.data == "menu")
async def _(callback: CallbackQuery, state: FSMContext):
    """Go menu"""

    await cmd_start(callback.message, state)
    await callback.message.delete()


@router.callback_query(F.data == "giveaway|list")
async def _(callback: CallbackQuery):
    """Giveaway list menu"""

    giveaways = await db.get_all_giveaways_user(callback.from_user.id)
    await callback.message.delete()
    await callback.message.answer_photo(
        photo='https://i.imgur.com/FRYuxCD.png',
        caption='<b>🎁 Список ваших розыгрышей:</b>',
        reply_markup=for_index.giveaway_list(giveaways)
    )
