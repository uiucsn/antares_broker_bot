import asyncio

from aiogram import Bot, Dispatcher, exceptions, types

from antares_broker_bot.config import TELEGRAM_API_TOKEN
from antares_broker_bot.db import USERS


BOT = Bot(token=TELEGRAM_API_TOKEN)
DP = Dispatcher(BOT)


@DP.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    USERS.add(message.from_user.id)
    await message.answer('Hello, ANTARES alert bot is starting to send you alerts')


async def send_message(user_id: int, text: str, disable_notification: bool = True) -> bool:
    try:
        await BOT.send_message(user_id, text, disable_notification=disable_notification)
        return True
    except exceptions.BotBlocked:
        return False
    except exceptions.ChatNotFound:
        return False
    except exceptions.RetryAfter as e:
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)
    except exceptions.UserDeactivated:
        return False
