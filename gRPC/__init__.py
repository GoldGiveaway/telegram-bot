import logging

import ujson as json
from urllib.parse import parse_qs
import gRPC.giveaway_pb2
import gRPC.giveaway_pb2_grpc
from services import db
import hashlib
import hmac
import base64
import settings
import hmac
import hashlib
from urllib.parse import unquote, parse_qs

def validate(hash_str, init_data, token, c_str="WebAppData"):
    init_data = sorted([ chunk.split("=")
          for chunk in unquote(init_data).replace('==&auth_date=', '%3D%3D&auth_date=').split("&")
            if chunk[:len("hash=")]!="hash="],
        key=lambda x: x[0])
    # TODO: Пофикси этот ужасный костыль
    init_data = "\n".join([f"{rec[0]}={rec[1]}".replace('%3D%3D', '==') for rec in init_data])

    secret_key = hmac.new(c_str.encode(), token.encode(),
        hashlib.sha256 ).digest()
    data_check = hmac.new( secret_key, init_data.encode(),
        hashlib.sha256)

    return data_check.hexdigest() == hash_str

settings = settings.Settings()

class Greeter(giveaway_pb2_grpc.GreeterServicer):
    async def SayGiveaway(self, request, context):
        initData = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(request.initData).items()}
        if not validate(initData['hash'], request.initData, settings.api_token.get_secret_value()):
            logging.info('initData invalid')
            return giveaway_pb2.GiveawayReply(json_message=json.dumps({'status': 'error', 'message': 'initData invalid'}))

        user = json.loads(initData['user'])

        db_user = await db.get_user(user['id'])
        if not db_user:
            await db.create_user(user['id'], user['username'], user['first_name'], user['last_name'])

        giveaway_id, chat_id = base64.b64decode(initData['start_param']).decode('utf-8').split('|', 2)
        result = await db.giveaway_participating(user['id'], giveaway_id)
        logging.info(f'User #{user["id"]} participating giveaway #{giveaway_id} - {result}')
        return giveaway_pb2.GiveawayReply(json_message=json.dumps({'status': 'success', 'message': 'Успех'}))
