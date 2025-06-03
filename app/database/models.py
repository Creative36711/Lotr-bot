from datetime import datetime
from sqlalchemy import Column, DateTime

from sqlalchemy import BigInteger, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

import os

engine = create_async_engine(os.environ['MYSQL_CONN'])

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Reactions(Base):
    __tablename__ = 'user_reactions'

    id: Mapped[int] = mapped_column(primary_key=True)
    message_id = mapped_column(BigInteger, unique=True)
    message_author_id = mapped_column(BigInteger)
    user_id = mapped_column(BigInteger)
    message_time = Column(DateTime, nullable=False, default=datetime.utcnow)


class Balance(Base):
    __tablename__ = 'user_balance'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger, unique=True)
    user_balance: Mapped[int] = Column(Integer)
    balance_time = Column(DateTime, nullable=False, default=datetime.utcnow)


class WatchedChannel(Base):
    __tablename__ = 'watched_channel'

    id: Mapped[int] = mapped_column(primary_key=True)
    can_ask_balance: Mapped[bool] = mapped_column(Boolean, default=False)
    reactions_tracked: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self):
        return f'Channel[{self.id}] can_ask_balance={self.can_ask_balance} reactions_tracked={self.reactions_tracked}'


async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
