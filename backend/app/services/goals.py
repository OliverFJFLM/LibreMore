from __future__ import annotations

from typing import Iterable
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Book, Goal, GoalBook


async def get_or_create_books(session: AsyncSession, isbns: Iterable[str]) -> list[Book]:
    books: list[Book] = []
    for idx, isbn in enumerate(isbns):
        isbn = isbn.strip()
        if not isbn:
            continue
        result = await session.execute(select(Book).where(Book.isbn13 == isbn))
        book = result.scalar_one_or_none()
        if not book:
            book = Book(isbn13=isbn, title=f"書籍 {isbn}")
            session.add(book)
            await session.flush()
        books.append(book)
    return books


async def attach_books_to_goal(session: AsyncSession, goal: Goal, books: list[Book]) -> None:
    for pos, book in enumerate(books, start=1):
        existing = next((gb for gb in goal.goal_books if gb.book_id == book.id), None)
        if existing:
            existing.position = pos
        else:
            goal.goal_books.append(
                GoalBook(goal_id=goal.id, book_id=book.id, position=pos, status="unread")
            )
    await session.flush()


async def compute_goal_progress(session: AsyncSession, goal_id: UUID) -> tuple[int, int]:
    stmt: Select = select(func.count(GoalBook.book_id), func.count().filter(GoalBook.status == "done")).where(
        GoalBook.goal_id == goal_id
    )
    result = await session.execute(stmt)
    total, done = result.one()
    return int(total or 0), int(done or 0)


def progress_ratio(total: int, done: int) -> float:
    if total == 0:
        return 0.0
    return round(done / total, 4)
