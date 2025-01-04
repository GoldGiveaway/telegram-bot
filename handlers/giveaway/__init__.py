from aiogram import Router
from . import create, edit

router = Router(name=__name__)
router.include_routers(create.router, edit.router)
