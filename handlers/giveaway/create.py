from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from filters.states import GiveawayCreate
from keyboards import for_index
from services import date, db
from datetime import timedelta

router = Router(name=__name__)


@router.callback_query(F.data == "giveaway|create")
async def _(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(GiveawayCreate.title)
    await callback.message.answer_photo(
        photo='https://i.imgur.com/erwWGOE.png',
        caption='<b>📝 Укажите название розыгрыша:</b>\n'
                '<i>* максимум 20 символов</i>\n\n'
                '<b>Пример:</b> iPhone 15',
        reply_markup=for_index.go_home()
    )


@router.message(GiveawayCreate.title)
async def _(message: Message, state: FSMContext):
    if len(message.text) > 20:
        await message.reply(f'<b>❗️ ОШИБКА:</b> Максимум 20 символов, а у Вас {len(message.text)}\n\n'
                            '<b>📝 Укажите название розыгрыша снова:</b>',
                            reply_markup=for_index.go_home())
        return

    await state.update_data({
        'title': message.text,
    })
    await state.set_state(GiveawayCreate.date)
    date_now = date.now_datetime()

    await message.answer_photo(
        photo='https://i.imgur.com/LuFRUue.png',
        caption='<b>📝 Укажите дату завершения розыгрыша:</b>\n\n'
                
                f'<blockquote><b>❗️ ВНИМАНИЕ:</b> Бот работает по часовому поясу MSK (GMT+3). '
                f'Актуальное время в боте: {date.date_to_string(date_now)}</blockquote>\n\n'
                
                f'<b>Пример:</b> {date.date_to_string(date_now + timedelta(days=1))}',
        reply_markup=for_index.go_home()
    )


@router.message(GiveawayCreate.date)
async def _(message: Message, state: FSMContext):
    try:
        date_end = date.string_to_date(message.text)
    except ValueError:
        await message.reply(f'<b>❗️ ОШИБКА:</b> Дата указана неверно\n\n'
                            '<b>📝 Укажите дату завершения розыгрыша снова:</b>',
                            reply_markup=for_index.go_home())
        return

    data = await state.get_data()
    await state.clear()
    await db.create_giveaway(
        title=data['title'],
        date_end=date_end,
        owner_id=message.from_user.id,
    )
    await message.answer('<b>🎁 Розыгрыш успешно создан!</b>')
