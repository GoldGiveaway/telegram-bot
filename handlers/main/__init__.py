from aiogram import Router
from . import menu, giveaway_create

router = Router(name=__name__)
router.include_routers(menu.router, giveaway_create.router)
