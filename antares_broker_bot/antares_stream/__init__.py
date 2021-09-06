import logging
from typing import Generator

from aioprocessing import AioQueue
from antares_client import StreamingClient
from antares_client._api.models import Locus

from antares_broker_bot.config import ANTARES_API_KEY, ANTARES_API_SECRET


def stream_alerts(topic: str) -> Generator[Locus, None, None]:
    with StreamingClient(topics=[topic], api_key=ANTARES_API_KEY, api_secret=ANTARES_API_SECRET) as client:
        for _topic, locus in client.iter():
            logging.info(f'Just recieved locus {locus.locus_id}')
            yield locus


def stream_alerts_to_queue(topic: str, queue: AioQueue) -> None:
    for locus in stream_alerts(topic):
        queue.put(locus)
