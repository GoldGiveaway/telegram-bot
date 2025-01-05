from aiogram import F, Bot
from aiogram.filters import BaseFilter, MagicData


ADMIN_ONLY = MagicData(F.event_from_user.id == F.settings.admin_id)
