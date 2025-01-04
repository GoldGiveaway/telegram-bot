import motor.motor_asyncio
from settings import Settings
from redis.asyncio import Redis
import time
from services import date

settings = Settings()
redis = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
)

class Database:
    def __init__(self, url_connect: str = None):
        self.cluster = motor.motor_asyncio.AsyncIOMotorClient(url_connect).cluster.TelegramBot

        self.users_collection = self.cluster.user
        self.giveaways_collection = self.cluster.giveaway

    async def create_user(self, user_id: int) -> dict:
        """
        Create a new user

        :param user_id: Telegram user id
        :return:
        """

        data = {
            'user_id': user_id,
            'created_at': date.now_datetime(),
        }

        await self.users_collection.insert_one(data)
        return data

    async def get_user(self, user_id: int) -> dict:
        """
        Get a user

        :param user_id: Telegram user id
        :return:
        """

        return await self.users_collection.find_one({'user_id': user_id})

    async def create_giveaway(self, title: str, date_end: date.datetime):
        data = {
            'created_at': date.now_datetime(),
            'end_et': date_end,
            'title': title,
            'description': '',
            'win_count': 1,
            # 'channels': [{'id': 123, 'message_id': 123, 'link': 'https://t.me/....', 'name': 'Супер канал'}],
            'channels': []
        }

        await self.giveaways_collection.insert_one(data)
        return data

db = Database(settings.mongodb_url.get_secret_value())
