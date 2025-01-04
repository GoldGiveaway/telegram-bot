from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup


class GiveawayCreate(StatesGroup):
    title = State()
    date = State()

NoneState = StateFilter(None)
AnyState = ~NoneState
