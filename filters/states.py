from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup


class GiveawayCreate(StatesGroup):
    title = State()
    date = State()

class ChatShared(StatesGroup):
    chat = State()

NoneState = StateFilter(None)
AnyState = ~NoneState
