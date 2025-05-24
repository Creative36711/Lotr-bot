from app.database.models import async_session, Reactions, Balance
from sqlalchemy import select, update, insert
from datetime import datetime
import logging
from typing import List
from sqlalchemy.ext.asyncio.session import AsyncSession


logger = logging.getLogger(__name__)

REACTION_COST = 10


async def ensure_balance(user_id: int, session: AsyncSession):
    result = await session.execute(
        select(Balance).where(Balance.user_id == user_id)
    )
    existing_balance = result.scalars().first()
    if not existing_balance:
        insert(Balance).values(user_id=user_id, user_balance=0)


async def add_user_reaction(message_id: int, message_author_id: int, user_id: int):
    session: AsyncSession
    async with async_session.begin() as session:
        existing_reaction = (await session.execute(
            select(Reactions).where(Reactions.message_id == message_id)
        )).scalars().first()
        if existing_reaction:
            logger.info(f'Повторная реакция на сообщение {message_id}')
            return
        new_reaction = Reactions(
            message_id=message_id,
            message_author_id=message_author_id,
            user_id=user_id,
        )
        session.add(new_reaction)
        await ensure_balance(message_author_id, session)
        await session.execute(
            update(Balance)
            .where(Balance.user_id == message_author_id)
            .values(
                user_balance=Balance.user_balance + REACTION_COST,
                balance_time=datetime.utcnow()
            )
        )


async def delete_user_reaction(message_id: int):
    session: AsyncSession
    async with async_session.begin() as session:
        reaction: Reactions = (await session.execute(
            select(Reactions).with_for_update().where(Reactions.message_id == message_id)
        )).scalars().first()
        if reaction:
            await session.delete(reaction)
            await session.execute(
                update(Balance)
                .where(Balance.user_id == reaction.message_author_id)
                .values(
                    user_balance=Balance.user_balance - REACTION_COST,
                    balance_time=datetime.utcnow()
                )
            )


async def add_user_balance(user_id: int):
    session: AsyncSession
    async with async_session.begin() as session:
        await ensure_balance(user_id, session)


async def get_balance(user_id: int) -> int:
    session: AsyncSession
    async with async_session() as session:
        await ensure_balance(user_id, session)
        result = await session.execute(
            select(Balance).where(Balance.user_id == user_id)
        )
        balance_obj = result.scalars().first()
        if balance_obj:
            return balance_obj.user_balance
        return 0


async def get_all_balances() -> List[Balance]:
    session: AsyncSession
    async with async_session() as session:
        return (await session.execute(
            select(Balance).order_by(Balance.user_id)
        )).scalars().all()


async def transfer_balance(sender_id: int, receiver_user_id: int, amount: int):
    """Передача баллов другому пользователю по нику."""
    session: AsyncSession
    async with async_session.begin() as session:
        # Получаем баланс отправителя
        result_sender = await session.execute(
            select(Balance).where(Balance.user_id == sender_id)
        )
        sender_balance_obj = result_sender.scalars().first()

        if not sender_balance_obj or sender_balance_obj.user_balance < amount:
            return False  # Недостаточно средств

        # Получаем баланс получателя или создаем его
        result_receiver = await session.execute(
            select(Balance).where(Balance.user_id == receiver_user_id)
        )
        receiver_balance_obj = result_receiver.scalars().first()

        if not receiver_balance_obj:
            receiver_balance_obj = Balance(
                user_id=receiver_user_id,
                user_balance=0,
            )
            session.add(receiver_balance_obj)

        # Обновляем балансы
        sender_balance_obj.user_balance -= amount
        receiver_balance_obj.user_balance += amount
    return True
