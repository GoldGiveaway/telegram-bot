from aiogram import Router
from . import menu, giveaway_create, giveaway_edit

router = Router(name=__name__)
router.include_routers(menu.router, giveaway_create.router, giveaway_edit.router)
