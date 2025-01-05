import uuid

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

    async def create_user(self, user_id: int, username: str, first_name: str, last_name: str) -> dict:
        """
        Create a new user

        :param user_id: Telegram user id
        :return:
        """

        data = {
            'user_id': user_id,
            'created_at': date.now_datetime(),
            'username': username,
            'last_name': last_name,
            'first_name': first_name,
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

    async def create_giveaway(self, title: str, date_end: date.datetime, owner_id: int):
        data = {
            'giveaway_id': str(uuid.uuid4()),
            'created_at': date.now_datetime(),
            'end_et': date_end,
            'title': title,
            'owner_id': owner_id,
            'description': '',
            'win_count': 1,
            # 'channels': [{'id': 123, 'message_id': 123, 'link': 'https://t.me/....', 'name': 'Супер канал', 'photo': ''}],
            'channels': [],
            # 'members': [{'id': 123, 'date': DATE}]
            'members': [],
            'last_message_update': None
        }

        await self.giveaways_collection.insert_one(data)
        return data

    async def get_giveaway(self, giveaway_id: str) -> dict:
        return await self.giveaways_collection.find_one({'giveaway_id': giveaway_id})

    async def update_giveaway(self, giveaway_id: str, js: dict):
        await self.giveaways_collection.update_one({'giveaway_id': giveaway_id}, {'$set': js})

    async def get_all_giveaways_user(self, user_id: int) -> list:
        return [item async for item in self.giveaways_collection.find({'owner_id': user_id})]

    async def giveaway_participating(self, user_id: int, giveaway_id: str) -> bool:
        giveaway_db = await self.get_giveaway(giveaway_id)
        if user_id in [member['id'] for member in giveaway_db['members']]:
            return False
        giveaway_db['members'].append({
            'id': user_id,
            'date': date.now_datetime(),
        })
        await self.update_giveaway(giveaway_id, giveaway_db)
        return True

db = Database(settings.mongodb_url.get_secret_value())
