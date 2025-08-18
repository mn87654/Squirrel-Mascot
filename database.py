# database.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, delete
from datetime import datetime, timezone
from settings import settings
from models import Base, User, Task, TaskCompletion

engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_or_create_user(tg_id: int, referred_by: Optional[int] = None):
    async with SessionLocal() as session:
        res = await session.execute(select(User).where(User.tg_id == tg_id))
        user = res.scalar_one_or_none()
        if user:
            return user, False
        user = User(tg_id=tg_id, referred_by=referred_by)
        session.add(user)
        await session.commit()
        return user, True

async def add_coins(tg_id: int, amount: int):
    async with SessionLocal() as session:
        res = await session.execute(select(User).where(User.tg_id == tg_id))
        user = res.scalar_one()
        user.coins += amount
        await session.commit()
        return user.coins

async def set_coins(tg_id: int, amount: int):
    async with SessionLocal() as session:
        res = await session.execute(select(User).where(User.tg_id == tg_id))
        user = res.scalar_one()
        user.coins = amount
        await session.commit()
        return user.coins

async def get_balance(tg_id: int) -> int:
    async with SessionLocal() as session:
        res = await session.execute(select(User.coins).where(User.tg_id == tg_id))
        return res.scalar_one_or_none() or 0

async def can_claim_daily(tg_id: int) -> bool:
    async with SessionLocal() as session:
        res = await session.execute(select(User).where(User.tg_id == tg_id))
        user = res.scalar_one()
        if user.last_daily is None:
            return True
        return (datetime.now(timezone.utc) - user.last_daily).total_seconds() >= 24 * 3600

async def claim_daily(tg_id: int, reward: int) -> int:
    async with SessionLocal() as session:
        res = await session.execute(select(User).where(User.tg_id == tg_id))
        user = res.scalar_one()
        user.coins += reward
        user.last_daily = datetime.now(timezone.utc)
        await session.commit()
        return user.coins

async def list_active_tasks():
    async with SessionLocal() as session:
        res = await session.execute(select(Task).where(Task.active == True))
        return res.scalars().all()

async def add_task(task_type: str, title: str, data: str, reward: int):
    async with SessionLocal() as session:
        t = Task(type=task_type, title=title, data=data, reward=reward, active=True)
        session.add(t)
        await session.commit()
        return t.id

async def remove_task(task_id: int):
    async with SessionLocal() as session:
        await session.execute(delete(Task).where(Task.id == task_id))
        await session.commit()

async def mark_task_complete(user_tg_id: int, task_id: int):
    async with SessionLocal() as session:
        tc = TaskCompletion(user_tg_id=user_tg_id, task_id=task_id)
        session.add(tc)
        res = await session.execute(select(Task.reward).where(Task.id == task_id))
        reward = res.scalar_one()
        resu = await session.execute(select(User).where(User.tg_id == user_tg_id))
        user = resu.scalar_one()
        user.coins += reward
        await session.commit()

async def completed_today(user_tg_id: int, task_id: int) -> bool:
    async with SessionLocal() as session:
        now = datetime.now(timezone.utc)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        res = await session.execute(
            select(TaskCompletion).where(
                TaskCompletion.user_tg_id == user_tg_id,
                TaskCompletion.task_id == task_id,
                TaskCompletion.completed_at >= start,
            )
        )
        return res.scalar_one_or_none
