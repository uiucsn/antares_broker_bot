import asyncio
import logging
from typing import Dict

from aiogram import Bot, Dispatcher, exceptions, executor, types
from aioprocessing import AioQueue

from antares_broker_bot.config import TELEGRAM_API_TOKEN
from antares_broker_bot.db import Db, DbIsNotStarted
from antares_broker_bot.locus import compose_message_from_locus


class TelegramBot:
    def __init__(self, db: Db):
        self.bot = Bot(token=TELEGRAM_API_TOKEN)
        self.dispatcher = Dispatcher(self.bot)
        self.db = db
        self.loop = None

        self.dispatcher.register_message_handler(self.start_cmd, commands=['start'])

    def run(self, loop: asyncio.AbstractEventLoop, queues: Dict[str, AioQueue]):
        self.loop = loop

        for topic, queue in queues.items():
            loop.create_task(self.broadcast_alerts(topic=topic, queue=queue))

        executor.start_polling(
            self.dispatcher,
            loop=loop,
            on_startup=self.on_startup,
            on_shutdown=self.on_shutdown,
        )

    async def on_startup(self, _dp):
        await self.db.on_startup()

    async def on_shutdown(self, _dp):
        await self.db.on_shutdown()

    async def broadcast_alerts(self, topic: str, queue: AioQueue) -> None:
        count = 0
        while True:
            try:
                users = await self.db.user_ids()
            except DbIsNotStarted:
                logging.warning("DB is not started but should be")
                await asyncio.sleep(0.1)
                continue
            locus = await queue.coro_get(loop=self.loop)
            msg = await compose_message_from_locus(locus)
            for user_id in users:
                if await self.db.add_locus_if_not_exists(user_id=user_id, topic_name=topic, locus_id=locus.locus_id):
                    if await self.send_message(user_id, msg):
                        count += 1

    async def start_cmd(self, message: types.Message):
        await self.db.add_user_by_id(message.from_user.id)  # we believe Db is started at this point
        await self.db.add_user_id_topic(message.from_user.id, 'iso_forest_anomaly_detection')
        await message.answer('Hello, ANTARES alert bot is starting to send you alerts')

    async def send_message(self, user_id: int, text: str, disable_notification: bool = True) -> bool:
        try:
            await self.bot.send_message(
                user_id,
                text,
                disable_notification=disable_notification,
                parse_mode="MarkdownV2"
            )
            return True
        except exceptions.BotBlocked:
            return False
        except exceptions.ChatNotFound:
            return False
        except exceptions.RetryAfter as e:
            await asyncio.sleep(e.timeout)
            return await self.send_message(user_id, text)
        except exceptions.UserDeactivated:
            return False
