import asyncio
import logging

import uvloop
from aiogram import executor
from aioprocessing import AioProcess, AioQueue

from antares_broker_bot.antares_stream import stream_alerts_to_queue
from antares_broker_bot.db import USERS
from antares_broker_bot.telegram_bot import DP, send_message


async def broadcast_alerts(topic) -> None:
    count = 0
    queue = AioQueue()
    p = AioProcess(target=stream_alerts_to_queue, args=(topic, queue))
    p.start()
    while True:
        locus = await queue.coro_get()
        for user_id in USERS:
            if await send_message(user_id, f'https://antares.noirlab.edu/loci/{locus.locus_id}'):
                count += 1
            await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)


def main():
    logging.basicConfig(level=logging.INFO)

    loop = uvloop.new_event_loop()
    loop.create_task(broadcast_alerts('iso_forest_anomaly_detection'))

    executor.start_polling(DP, loop=loop)


if __name__ == '__main__':
    main()
