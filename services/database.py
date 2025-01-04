import motor.motor_asyncio
from settings import Settings
from redis.asyncio import Redis
import time

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

    async def create_user(self, user_id: int) -> dict:
        """
        Create a new user

        :param user_id: Telegram user id
        :return:
        """

        data = {
            'user_id': user_id,
            'created_at': time.time(),
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

db = Database(settings.mongodb_url.get_secret_value())
