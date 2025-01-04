from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from filters.states import ChatShared
from keyboards import for_giveaway_edit, for_index
from services import date, db
from services.giveaway_text import generate_giveaway_text, generate_image_url
from settings import Settings

router = Router(name=__name__)

async def open_giveaway(message: Message, giveaway_db: dict):
    await message.answer_photo(
        photo=generate_image_url(giveaway_db),
        caption=generate_giveaway_text(giveaway_db),
        reply_markup=for_giveaway_edit.giveaway_edit(giveaway_db['giveaway_id'])
    )

@router.callback_query(F.data.startswith("giveaway|edit|"))
async def _(callback: CallbackQuery, state: FSMContext):
    giveaway_id = callback.data.split("|")[2]
    giveaway_db = await db.get_giveaway(giveaway_id)

    await callback.message.delete()
    await open_giveaway(callback.message, giveaway_db)



@router.callback_query(F.data.startswith("gedit|channel|"))
async def _(callback: CallbackQuery, state: FSMContext):
    giveaway_id = callback.data.split("|")[2]


    await state.set_state(ChatShared.chat)
    await state.update_data({'giveaway_id': giveaway_id})
    await callback.message.reply('<b>📢 Нажмите кнопку ниже что-бы подключить канал</b>',
                                 reply_markup=for_giveaway_edit.add_channel())


@router.message(ChatShared.chat, F.chat_shared)
async def _(message: Message, state: FSMContext):
    data = await state.get_data()
    giveaway_db = await db.get_giveaway(data['giveaway_id'])
    await state.clear()

    channel = message.chat_shared
    if channel.chat_id in [channel['id'] for channel in giveaway_db['channels']]:
        await message.answer('<b>Этот канал уже был добавлен!</b>', reply_markup=for_index.clear_keyboard())
    else:
        photo_id = None
        if channel.photo:
            photo_id = channel.photo[0].file_id
        giveaway_db['channels'].append({'id': channel.chat_id, 'message_id': None, 'link': None, 'name': channel.title, 'photo': photo_id})
        await db.update_giveaway(giveaway_db['giveaway_id'], giveaway_db)

        await message.answer('<b>Канал успешно добавлен!</b>', reply_markup=for_index.clear_keyboard())
    await open_giveaway(message, giveaway_db)
