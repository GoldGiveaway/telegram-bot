import motor.motor_asyncio
from settings import Settings
from redis.asyncio import Redis
from datetime import timedelta, datetime, timezone
from services import date
from interface.giveaway import IGiveaway, IMember
from interface.user import IUser

class ObjectNotFound(Exception):
    pass


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

    async def create_user(self, user_id: int, username: str, first_name: str, last_name: str) -> IUser:
        """
        Create a new user

        :param user_id: Telegram user id
        :return:
        """

        data = IUser(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        await self.users_collection.insert_one(data.model_dump())
        return data

    async def get_user(self, user_id: int) -> IUser:
        """
        Get a user

        :param user_id: Telegram user id
        :return:
        """

        data = await self.users_collection.find_one({'user_id': user_id})
        if data:
            return IUser(**data)
        raise ObjectNotFound()

    async def create_giveaway(self, title: str, date_end: date.datetime, owner_id: int) -> IGiveaway:
        data = IGiveaway(
            end_et=date_end,
            title=title,
            owner_id=owner_id,
        )

        await self.giveaways_collection.insert_one(data.model_dump())
        return data

    async def get_giveaway(self, giveaway_id: str) -> IGiveaway:
        data = await self.giveaways_collection.find_one({'giveaway_id': giveaway_id})
        if data:
            return IGiveaway(**data)
        raise ObjectNotFound()

    async def update_giveaway(self, giveaway_id: str, js: dict):
        await self.giveaways_collection.update_one({'giveaway_id': giveaway_id}, {'$set': js})

    async def get_all_giveaways_user(self, user_id: int) -> list:
        return [item async for item in self.giveaways_collection.find({'owner_id': user_id})]

    async def get_all_update_giveaways(self):
        return [IGiveaway(**data) async for data in self.giveaways_collection.find({
            '$or': [
                {
                    '$or': [
                        {'last_message_update': None},
                        {'last_message_update': {'$lt': datetime.now() - timedelta(hours=5)}}
                    ]
                },
                {'end_et': {'$gt': datetime.now()}}
            ],
            'status': 'active'
        })]

    async def giveaway_participating(self, user_id: int, giveaway_id: str) -> bool:
        giveaway_db = await self.get_giveaway(giveaway_id)
        if user_id in [member.id for member in giveaway_db.members]:
            return False
        giveaway_db.members.append(IMember(id=user_id, date=datetime.now()))
        giveaway_db.last_message_update = None
        await self.update_giveaway(giveaway_id, giveaway_db.model_dump())
        return True

db = Database(settings.mongodb_url.get_secret_value())
