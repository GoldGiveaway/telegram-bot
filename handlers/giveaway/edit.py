from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from filters.states import ChatShared, GiveawayEdit
from keyboards import for_giveaway_edit, for_index
from services import date, db
from services.giveaway_text import generate_giveaway_text, generate_image_url, generate_button_link
from datetime import timedelta

router = Router(name=__name__)

async def open_giveaway(message: Message, giveaway_db: dict):
    await message.answer_photo(
        photo=generate_image_url(giveaway_db),
        caption=generate_giveaway_text(giveaway_db),
        reply_markup=for_giveaway_edit.giveaway_edit(giveaway_db['giveaway_id'])
    )

async def send_giveaway(channel_id: int, giveaway_db: dict, bot: Bot) -> int:
    bot_me = await bot.get_me()
    msg = await bot.send_photo(
        chat_id=channel_id,
        photo=generate_image_url(giveaway_db),
        caption=generate_giveaway_text(giveaway_db),
        reply_markup=for_giveaway_edit.giveaway_publish(
            generate_button_link(bot_me.username, giveaway_db['giveaway_id'], channel_id))
    )
    return msg.message_id

@router.callback_query(F.data.startswith("giveaway|edit|"))
async def _(callback: CallbackQuery, state: FSMContext):
    giveaway_id = callback.data.split("|")[2]
    giveaway_db = await db.get_giveaway(giveaway_id)

    await callback.message.delete()
    await open_giveaway(callback.message, giveaway_db)

@router.callback_query(F.data.startswith("resend|"))
async def _(callback: CallbackQuery, state: FSMContext, bot: Bot):
    _, giveaway_id, channel_id = callback.data.split("|")
    giveaway_db = await db.get_giveaway(giveaway_id)

    msg_id = await send_giveaway(int(channel_id), giveaway_db, bot)
    for channel in giveaway_db['channels']:
        if channel['id'] == channel_id:
            channel['message_id'] = msg_id
            break
    await db.update_giveaway(giveaway_id, {'channels': giveaway_db['channels']})
    await callback.message.reply('Опубликовано!')


@router.callback_query(F.data.startswith("gedit|publish|"))
async def _(callback: CallbackQuery, state: FSMContext, bot: Bot):
    giveaway_id = callback.data.split("|")[2]
    giveaway_db = await db.get_giveaway(giveaway_id)

    channels = []

    for channel in giveaway_db['channels']:
        channel['message_id'] = await send_giveaway(
            channel['id'],
            giveaway_db,
            bot
        )
        channels.append(channel)

    await db.update_giveaway(giveaway_id, {'channels': channels, 'last_message_update': None, 'status': 'active'})
    await callback.message.reply('Успешно!')

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
    if channel.chat_id in [channel['id'] for channel in giveaway_db['channels']]:
        await message.answer('<b>Этот канал уже был добавлен!</b>', reply_markup=for_index.clear_keyboard())
    else:
        photo_id = None
        if channel.photo:
            photo_id = channel.photo[0].file_id
        link = await bot.create_chat_invite_link(channel.chat_id)
        giveaway_db['channels'].append({'id': channel.chat_id, 'message_id': None, 'link': link.invite_link, 'name': channel.title, 'photo': photo_id})
        await db.update_giveaway(giveaway_db['giveaway_id'], giveaway_db)

        await message.answer('<b>Канал успешно добавлен!</b>', reply_markup=for_index.clear_keyboard())
    await open_giveaway(message, giveaway_db)



@router.callback_query(F.data.startswith("gedit|"))
async def _(callback: CallbackQuery, state: FSMContext):
    giveaway_id = callback.data.split("|")[2]
    type_edit = callback.data.split("|")[1]

    # TODO: Сделать нормально
    match type_edit:
        case 'title':
            text = '<b>📝 Укажите название розыгрыша:</b>\n' \
                '<i>* максимум 20 символов</i>\n\n' \
                '<b>Пример:</b> iPhone 15'
        case 'description':
            text = '<b>📝 Укажите описание розыгрыша:</b>\n' \
                   '<i>* максимум 2 000 символов</i>'
        case 'date':
            date_now = date.now_datetime()
            text = '<b>📝 Укажите дату завершения розыгрыша:</b>\n\n' \
                f'<blockquote><b>❗️ ВНИМАНИЕ:</b> Бот работает по часовому поясу MSK (GMT+3). ' \
                f'Актуальное время в боте: {date.date_to_string(date_now)}</blockquote>\n\n' \
                f'<b>Пример:</b> {date.date_to_string(date_now + timedelta(days=1))}'
        case 'win':
            text = '<b>📝 Укажите количество победителей розыгрыша:</b>\n' \
                   '<i>* максимум 50 человек</i>'
        case _:
            return

    await state.set_state(GiveawayEdit.data)
    await state.update_data({
        'giveaway_id': giveaway_id,
        'message_id': callback.message.message_id,
        'type': type_edit,
    })
    await callback.message.reply(text, reply_markup=for_index.go_home())


@router.message(GiveawayEdit.data)
async def _(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    giveaway_db = await db.get_giveaway(data['giveaway_id'])

    # TODO: Сделать нормально
    match data['type']:
        case 'title':
            if len(message.text) > 20:
                await message.reply(f'<b>❗️ ОШИБКА:</b> Максимум 20 символов, а у Вас {len(message.text)}\n\n'
                                    '<b>📝 Укажите название розыгрыша снова:</b>',
                                    reply_markup=for_index.go_home())
                return
            giveaway_db['title'] = message.text
        case 'description':
            if len(message.text) > 2000:
                await message.reply(f'<b>❗️ ОШИБКА:</b> Максимум 2 000 символов, а у Вас {len(message.text)}\n\n'
                                    '<b>📝 Укажите описание розыгрыша снова:</b>',
                                    reply_markup=for_index.go_home())
                return
            giveaway_db['description'] = message.text
        case 'win':
            if not message.text.isdigit():
                await message.reply(f'<b>❗️ ОШИБКА:</b> Вы указали число с ошибкой\n\n'
                                    '<b>📝 Укажите количество победителей розыгрыша снова:</b>',
                                    reply_markup=for_index.go_home())
                return
            if int(message.text) > 50:
                await message.reply(f'<b>❗️ ОШИБКА:</b> Максимум 50 человек, а Вы указали {message.text}\n\n'
                                    '<b>📝 Укажите количество победителей розыгрыша снова:</b>',
                                    reply_markup=for_index.go_home())
                return
            giveaway_db['win_count'] = int(message.text)
        case 'date':
            try:
                date_end = date.string_to_date(message.text)
            except ValueError:
                await message.reply(f'<b>❗️ ОШИБКА:</b> Дата указана неверно\n\n'
                                    '<b>📝 Укажите дату завершения розыгрыша снова:</b>',
                                    reply_markup=for_index.go_home())
                return
            giveaway_db['end_et'] = date_end
        case _: return

    await state.clear()
    giveaway_db['last_message_update'] = None
    await db.update_giveaway(giveaway_db['giveaway_id'], giveaway_db)
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=data['message_id']
    )
    await open_giveaway(message, giveaway_db)
