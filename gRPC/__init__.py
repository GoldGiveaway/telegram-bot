import logging
import ujson as json
import gRPC.giveaway_pb2
import gRPC.giveaway_pb2_grpc
from services import db, ObjectNotFound
import base64
import settings

settings = settings.Settings()

class Greeter(giveaway_pb2_grpc.GreeterServicer):
    async def GetGiveaway(self, request, context):
        initData = json.loads(request.initData)
        giveaway_id, chat_id = base64.b64decode(initData['start_param']).decode('utf-8').split('|', 2)
        giveaway_db = await db.get_giveaway(giveaway_id)
        return giveaway_pb2.GiveawayReply(json_message=json.dumps({'channels': giveaway_db.channels}))

    async def ParticipatingGiveaway(self, request, context):
        initData = json.loads(request.initData)
        user = json.loads(initData['user'])

        try:
            await db.get_user(int(user['id']))
        except ObjectNotFound:
            await db.create_user(int(user['id']), user['username'], user['first_name'], user['last_name'])

        giveaway_id, chat_id = base64.b64decode(initData['start_param']).decode('utf-8').split('|', 2)
        result = await db.giveaway_participating(user['id'], giveaway_id)
        logging.info(f'User #{user["id"]} participating giveaway #{giveaway_id} - {result}')
        return giveaway_pb2.GiveawayReply(json_message=json.dumps({'status': True}))
