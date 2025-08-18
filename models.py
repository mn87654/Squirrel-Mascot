# models.py
from typing import Optional
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Integer, BigInteger, String, ForeignKey, DateTime, Boolean, UniqueConstraint
from datetime import datetime, timezone

Base = declarative_base()

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    coins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    referred_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.tg_id"), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_daily: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    data: Mapped[str] = mapped_column(String)
    reward: Mapped[int] = mapped_column(Integer, default=100)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class TaskCompletion(Base):
    __tablename__ = "task_completions"
    __table_args__ = (
        UniqueConstraint("user_tg_id", "task_id", "completed_at", name="uq_user_task_day"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_tg_id: Mapped[int] = mapped_column(BigInteger, index=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"))
    completed_at: Mapped[datetime] = mapped_column(timezone(timezone=True), default=utcnow)
