import asyncio
import logging
from typing import Set

from sqlalchemy import and_, engine, exists, select
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from antares_broker_bot.config import SQL_HOSTNAME, SQL_USERNAME, SQL_DATABASE, SQL_PASSWORD
from .tables import Base, Locus, Topic, User


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
        async with AsyncSession(self.engine) as session, session.begin():
            session.merge(User(user_id=user_id))

    async def add_user_id_topic(self, user_id: int, topic_name: str):
        self.check_started()
        async with AsyncSession(self.engine) as session, session.begin():
            topic = (await session.execute(select(Topic).where(and_(
                Topic.user_id == user_id,
                Topic.topic == topic_name,
            )))).scalar()
            if topic is not None:
                return
            session.add(Topic(user=User(user_id=user_id), topic=topic_name))

    async def add_locus_if_not_exists(self, user_id: int, topic_name: str, locus_id: str) -> bool:
        async with AsyncSession(self.engine) as session, session.begin():
            topic = (await session.execute(select(Topic).where(and_(
                Topic.user_id == user_id,
                Topic.topic == topic_name,
            )))).scalar()
            if topic is None:
                logging.warning(f'Topic {topic_name} is not found for user {user_id}')
                return False
            locus = (await session.execute(select(Locus).where(and_(
                Locus.topic_id == topic.id,
                Locus.locus_id == locus_id,
            )))).scalar()
            if locus is not None:
                return False
            session.add(Locus(topic_id=topic.id, locus_id=locus_id))
        return True
