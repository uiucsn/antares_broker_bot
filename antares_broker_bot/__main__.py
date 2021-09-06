import logging
import time
from typing import Dict, Iterable, Mapping

import uvloop
from aioprocessing import AioProcess, AioQueue

from antares_broker_bot.antares_stream import stream_alerts_to_queue
from antares_broker_bot.db import Db
from antares_broker_bot.telegram_bot import TelegramBot


def create_queues(topics: Iterable[str]) -> Dict[str, AioQueue]:
    return {topic: AioQueue() for topic in topics}


def launch_antares_processes(queues: Mapping[str, AioQueue]) -> None:
    for topic, queue in queues.items():
        p = AioProcess(target=stream_alerts_to_queue, args=(topic, queue))
        p.start()


def main():
    logging.basicConfig(level=logging.INFO)

    loop = uvloop.new_event_loop()

    db = Db(echo=True)

    bot = TelegramBot(db=db)

    queues = create_queues(['iso_forest_anomaly_detection'])
    launch_antares_processes(queues)

    loop.run_until_complete(db.wait_db_is_ready())

    bot.run(loop=loop, queues=queues)


if __name__ == '__main__':
    main()
