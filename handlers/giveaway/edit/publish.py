from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards import for_giveaway_edit
from services import db
from interface.giveaway import IGiveaway
from services.giveaway_text import generate_giveaway_text, generate_image_url, generate_button_link

router = Router(name=__name__)

async def send_giveaway(channel_id: int, giveaway_db: IGiveaway, bot: Bot) -> int:
    bot_me = await bot.get_me()
    msg = await bot.send_photo(
        chat_id=channel_id,
        photo=generate_image_url(giveaway_db),
        caption=generate_giveaway_text(giveaway_db),
        reply_markup=for_giveaway_edit.giveaway_publish(
            generate_button_link(bot_me.username, giveaway_db.giveaway_id, channel_id))
    )
    return msg.message_id


@router.callback_query(F.data.startswith("resend|"))
async def _(callback: CallbackQuery, state: FSMContext, bot: Bot):
    _, giveaway_id, channel_id = callback.data.split("|")
    giveaway_db = await db.get_giveaway(giveaway_id)

    msg_id = await send_giveaway(int(channel_id), giveaway_db, bot)
    for channel in giveaway_db.channels:
        if channel.id == channel_id:
            channel.message_id = msg_id
            break
    await db.update_giveaway(giveaway_id, {'channels': giveaway_db.channels})
    await callback.message.reply('Опубликовано!')


@router.callback_query(F.data.startswith("gedit|publish|"))
async def _(callback: CallbackQuery, state: FSMContext, bot: Bot):
    giveaway_id = callback.data.split("|")[2]
    giveaway_db = await db.get_giveaway(giveaway_id)

    channels = []

    for channel in giveaway_db.channels:
        channel.message_id = await send_giveaway(channel.id, giveaway_db, bot)
        channels.append(channel)

    await db.update_giveaway(giveaway_id, {'channels': channels, 'last_message_update': None, 'status': 'active'})
    await callback.message.reply('Успешно!')
