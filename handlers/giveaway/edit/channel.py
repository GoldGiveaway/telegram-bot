from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from filters.states import ChatShared
from keyboards import for_index, for_giveaway_edit
from .general import open_giveaway
from services import db
from interface.giveaway import IChannel

router = Router(name=__name__)

@router.callback_query(F.data.startswith("gedit|channel|"))
async def _(callback: CallbackQuery, state: FSMContext):
    giveaway_id = callback.data.split("|")[2]


    await state.set_state(ChatShared.chat)
    await state.update_data({'giveaway_id': giveaway_id})
    await callback.message.reply('<b>📢 Нажмите кнопку ниже что-бы подключить канал</b>',
                                 reply_markup=for_giveaway_edit.add_channel())


@router.message(ChatShared.chat, F.chat_shared)
async def _(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    giveaway_db = await db.get_giveaway(data['giveaway_id'])
    await state.clear()

    channel = message.chat_shared
    if channel.chat_id in [channel.id for channel in giveaway_db.channels]:
        await message.answer('<b>Этот канал уже был добавлен!</b>', reply_markup=for_index.clear_keyboard())
    else:
        photo_id = None
        if channel.photo:
            photo_id = channel.photo[0].file_id
        link = await bot.create_chat_invite_link(channel.chat_id)
        giveaway_db.channels.append(
            IChannel(id=channel.chat_id, message_id=None, link=link.invite_link, name=channel.title, photo=photo_id)
        )
        await db.update_giveaway(giveaway_db.giveaway_id, giveaway_db.model_dump())

        await message.answer('<b>Канал успешно добавлен!</b>', reply_markup=for_index.clear_keyboard())
    await open_giveaway(message, giveaway_db)
