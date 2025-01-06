from aiogram.types import CallbackQuery
from services import db
from . import general, channel, publish
from aiogram import Router, F

router = Router(name=__name__)
router.include_routers(general.router, channel.router, publish.router)

@router.callback_query(F.data.startswith("giveaway|edit|"))
async def _(callback: CallbackQuery):
    giveaway_id = callback.data.split("|")[2]
    giveaway_db = await db.get_giveaway(giveaway_id)
    await callback.message.delete()
    await general.open_giveaway(callback.message, giveaway_db)
