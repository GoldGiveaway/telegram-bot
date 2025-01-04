from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from services import redis
from handlers import routers
import ujson
from settings import Settings
from middlewares import UserDBMiddleware


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(
        name="main_dispatcher",
        storage=RedisStorage(redis=redis, json_loads=ujson.decode, json_dumps=ujson.encode),
        redis=redis,
    )
    dp["settings"] = Settings()
    dp.include_routers(*routers)
    dp.update.outer_middleware(UserDBMiddleware())

    dp.callback_query.middleware(CallbackAnswerMiddleware())

    return dp


def create_bot(settings: Settings) -> Bot:
    session = AiohttpSession(json_loads=ujson.decode, json_dumps=ujson.encode)
    return Bot(
        token=settings.api_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )
