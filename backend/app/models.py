from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def uuid_pk() -> UUID:
    return uuid4()


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pk)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    goals: Mapped[list[Goal]] = relationship("Goal", back_populates="user", cascade="all, delete-orphan")


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pk)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    due_date: Mapped[Optional[date]] = mapped_column(Date)

    user: Mapped[User] = relationship("User", back_populates="goals")
    goal_books: Mapped[list[GoalBook]] = relationship(
        "GoalBook",
        back_populates="goal",
        cascade="all, delete-orphan",
        order_by="GoalBook.position",
    )


class Book(Base):
    __tablename__ = "books"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pk)
    isbn13: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[Optional[str]] = mapped_column(String)
    publisher: Mapped[Optional[str]] = mapped_column(String)
    pubyear: Mapped[Optional[int]] = mapped_column(Integer)
    ndc: Mapped[Optional[str]] = mapped_column(String)
    ndlc: Mapped[Optional[str]] = mapped_column(String)

    goal_books: Mapped[list[GoalBook]] = relationship("GoalBook", back_populates="book")


class GoalBook(Base):
    __tablename__ = "goal_books"
    __table_args__ = (UniqueConstraint("goal_id", "book_id", name="uq_goal_book"),)

    goal_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), primary_key=True)
    book_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id"), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="unread")
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    goal: Mapped[Goal] = relationship("Goal", back_populates="goal_books")
    book: Mapped[Book] = relationship("Book", back_populates="goal_books")
