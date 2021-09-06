import asyncio
from typing import Set

from sqlalchemy import engine, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from antares_broker_bot.config import SQL_HOSTNAME, SQL_USERNAME, SQL_DATABASE, SQL_PASSWORD
from .tables import Base, User


class DbIsNotStarted(RuntimeError):
    pass


class Db:
    def __init__(self, url=None, echo=False):
        if url is None:
            url = engine.URL.create(
                drivername='postgresql+asyncpg',
                username=SQL_USERNAME,
                password=SQL_PASSWORD,
                host=SQL_HOSTNAME,
                database=SQL_DATABASE,
            )
        self.engine = create_async_engine(url, echo=echo)
        self.started = False

    async def wait_db_is_ready(self):
        while True:
            try:
                async with self.engine.begin():
                    pass
                return
            except DBAPIError:
                await asyncio.sleep(0.1)

    async def on_startup(self):
        self.started = True
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def on_shutdown(self):
        await self.engine.dispose()

    def check_started(self):
        if not self.started:
            raise DbIsNotStarted

    # TODO: cache it
    async def user_ids(self) -> Set[int]:
        self.check_started()
        async with AsyncSession(self.engine) as session:
            result = await session.execute(select(User.user_id))
            return set(result.scalars())

    async def add_user_by_id(self, user_id: int):
        self.check_started()
        async with AsyncSession(self.engine) as session:
            exists = (await session.execute(
                select(User).where(User.user_id == user_id)
            )).scalar() is not None
            if not exists:
                with session.begin():
                    session.add(User(user_id=user_id))
