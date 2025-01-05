from aiogram import Router
from . import menu
from filters.chat import ADMIN_ONLY

router = Router(name=__name__)

router.message.filter(ADMIN_ONLY)
router.callback_query.filter(ADMIN_ONLY)

router.include_routers(menu.router)
