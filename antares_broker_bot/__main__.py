import asyncio
import logging
from typing import Dict, Iterable, Mapping

import uvloop
from aiogram import executor
from aioprocessing import AioProcess, AioQueue

from antares_broker_bot.antares_stream import stream_alerts_to_queue
from antares_broker_bot.db import USERS
from antares_broker_bot.locus import compose_message_from_locus
from antares_broker_bot.telegram_bot import DP, send_message


def create_queues(topics: Iterable[str]) -> Dict[str, AioQueue]:
    return {topic: AioQueue() for topic in topics}


def launch_antares_processes(queues: Mapping[str, AioQueue]) -> None:
    for topic, queue in queues.items():
        p = AioProcess(target=stream_alerts_to_queue, args=(topic, queue))
        p.start()


async def broadcast_alerts(queue) -> None:
    count = 0
    while True:
        locus = await queue.coro_get()
        msg = await compose_message_from_locus(locus)
        for user_id in USERS:
            if await send_message(user_id, msg):
                count += 1


def main():
    logging.basicConfig(level=logging.INFO)

    queues = create_queues(['iso_forest_anomaly_detection'])
    launch_antares_processes(queues)

    loop = uvloop.new_event_loop()

    for queue in queues.values():
        loop.create_task(broadcast_alerts(queue))

    executor.start_polling(DP, loop=loop)


if __name__ == '__main__':
    main()
