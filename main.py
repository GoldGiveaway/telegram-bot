import asyncio
import logging
from factory import create_dispatcher, create_bot
from typing import cast
from settings import Settings
import grpc
import gRPC

logging.basicConfig(level=logging.INFO)


async def run_grpc_server():
    server = grpc.aio.server()
    gRPC.giveaway_pb2_grpc.add_GreeterServicer_to_server(gRPC.Greeter(), server)
    server.add_insecure_port("[::]:50051")
    logging.info("gRPC server is running on port 50051")
    await server.start()
    await server.wait_for_termination()

async def run_bot():
    dp = create_dispatcher()
    bot = create_bot(settings=cast(Settings, dp["settings"]))

    bot_task = dp.start_polling(bot)
    grpc_task = run_grpc_server()

    return await asyncio.gather(bot_task, grpc_task)


if __name__ == '__main__':
    asyncio.run(run_bot())