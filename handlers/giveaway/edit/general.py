from datetime import timedelta
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from filters.states import GiveawayEdit
from keyboards import for_index
from services import date, db
from interface.giveaway import IGiveaway
from services.giveaway_text import generate_giveaway_text, generate_image_url
from keyboards import for_giveaway_edit

router = Router(name=__name__)

async def open_giveaway(message: Message, giveaway_db: IGiveaway) -> None:
    """Send message edit panel giveaway"""

    await message.answer_photo(
        photo=generate_image_url(giveaway_db),
        caption=generate_giveaway_text(giveaway_db),
        reply_markup=for_giveaway_edit.giveaway_edit(giveaway_db.giveaway_id, giveaway_db.status),
    )

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
            giveaway_db.title = message.text
        case 'description':
            if len(message.text) > 2000:
                await message.reply(f'<b>❗️ ОШИБКА:</b> Максимум 2 000 символов, а у Вас {len(message.text)}\n\n'
                                    '<b>📝 Укажите описание розыгрыша снова:</b>',
                                    reply_markup=for_index.go_home())
                return
            giveaway_db.description = message.text
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
            giveaway_db.win_count = int(message.text)
        case 'date':
            try:
                date_end = date.string_to_date(message.text)
            except ValueError:
                await message.reply(f'<b>❗️ ОШИБКА:</b> Дата указана неверно\n\n'
                                    '<b>📝 Укажите дату завершения розыгрыша снова:</b>',
                                    reply_markup=for_index.go_home())
                return
            giveaway_db.end_et = date_end
        case _: return

    await state.clear()
    giveaway_db.last_message_update = None
    await db.update_giveaway(giveaway_db.giveaway_id, giveaway_db.model_dump())
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=data['message_id']
    )
    await open_giveaway(message, giveaway_db)
