import asyncio
import logging
from factory import create_dispatcher, create_bot
from typing import cast
from settings import Settings

logging.basicConfig(level=logging.INFO)


async def run_bot():
    dp = create_dispatcher()
    bot = create_bot(settings=cast(Settings, dp["settings"]))

    return await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(run_bot())