from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..deps import get_current_user, get_db
from ..models import Book, Goal, GoalBook, User
from ..services.goals import attach_books_to_goal, compute_goal_progress, get_or_create_books, progress_ratio

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("", response_model=schemas.GoalOut)
async def create_goal(
    payload: schemas.GoalCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> schemas.GoalOut:
    goal = Goal(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        due_date=payload.due_date,
    )
    session.add(goal)
    await session.flush()

    books = await get_or_create_books(session, payload.recommended_isbns)
    await attach_books_to_goal(session, goal, books)
    await session.commit()

    total, done = await compute_goal_progress(session, goal.id)
    return schemas.GoalOut(
        id=goal.id,
        title=goal.title,
        description=goal.description,
        due_date=goal.due_date,
        created_at=goal.created_at,
        updated_at=goal.updated_at,
        archived=goal.archived,
        progress=progress_ratio(total, done),
        total_books=total,
        done_books=done,
    )


async def goal_to_detail(session: AsyncSession, goal: Goal) -> schemas.GoalDetailOut:
    total, done = await compute_goal_progress(session, goal.id)
    books = []
    for gb in goal.goal_books:
        book = gb.book
        books.append(
            schemas.GoalBookOut(
                book=schemas.BookOut(
                    isbn13=book.isbn13,
                    title=book.title,
                    author=book.author,
                    publisher=book.publisher,
                    pubyear=book.pubyear,
                    ndc=book.ndc,
                    ndlc=book.ndlc,
                    reason=None,
                ),
                status=gb.status,
                position=gb.position,
                completed_at=gb.completed_at,
            )
        )
    return schemas.GoalDetailOut(
        id=goal.id,
        title=goal.title,
        description=goal.description,
        due_date=goal.due_date,
        created_at=goal.created_at,
        updated_at=goal.updated_at,
        archived=goal.archived,
        progress=progress_ratio(total, done),
        total_books=total,
        done_books=done,
        books=sorted(books, key=lambda x: x.position),
    )


@router.get("/{goal_id}", response_model=schemas.GoalDetailOut)
async def get_goal(
    goal_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> schemas.GoalDetailOut:
    goal = await session.get(Goal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Goal not found")
    await session.refresh(goal, attribute_names=["goal_books"])
    for gb in goal.goal_books:
        await session.refresh(gb, attribute_names=["book"])
    return await goal_to_detail(session, goal)


@router.patch("/{goal_id}/books/{isbn13}", response_model=schemas.GoalProgressResponse)
async def update_goal_book_status(
    goal_id: UUID,
    isbn13: str,
    payload: schemas.GoalBookStatusUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> schemas.GoalProgressResponse:
    stmt = (
        select(GoalBook)
        .join(Goal, Goal.id == GoalBook.goal_id)
        .join(Book, Book.id == GoalBook.book_id)
        .where(GoalBook.goal_id == goal_id, Book.isbn13 == isbn13, Goal.user_id == current_user.id)
    )
    result = await session.execute(stmt)
    goal_book = result.scalar_one_or_none()
    if not goal_book:
        raise HTTPException(status_code=404, detail="Book not found in goal")
    goal_book.status = payload.status
    if payload.status == "done":
        goal_book.completed_at = datetime.utcnow()
    else:
        goal_book.completed_at = None
    await session.commit()
    total, done = await compute_goal_progress(session, goal_id)
    return schemas.GoalProgressResponse(progress=progress_ratio(total, done), total_books=total, done_books=done)


@router.patch("/{goal_id}/archive", response_model=schemas.GoalOut)
async def archive_goal(
    goal_id: UUID,
    payload: schemas.GoalArchivePayload,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> schemas.GoalOut:
    goal = await session.get(Goal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Goal not found")
    goal.archived = payload.archived
    goal.updated_at = datetime.utcnow()
    await session.commit()
    total, done = await compute_goal_progress(session, goal.id)
    return schemas.GoalOut(
        id=goal.id,
        title=goal.title,
        description=goal.description,
        due_date=goal.due_date,
        created_at=goal.created_at,
        updated_at=goal.updated_at,
        archived=goal.archived,
        progress=progress_ratio(total, done),
        total_books=total,
        done_books=done,
    )
