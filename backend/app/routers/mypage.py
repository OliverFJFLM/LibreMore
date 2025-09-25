from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..deps import get_current_user, get_db
from ..models import Goal, User
from ..services.goals import compute_goal_progress, progress_ratio

router = APIRouter(prefix="/mypage", tags=["mypage"])


@router.get("/goals")
async def list_goals(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    include_archived: bool = Query(default=False),
) -> dict:
    stmt = select(Goal).where(Goal.user_id == current_user.id)
    if not include_archived:
        stmt = stmt.where(Goal.archived.is_(False))
    stmt = stmt.order_by(Goal.created_at.desc())
    result = await session.execute(stmt)
    goals = result.scalars().unique().all()
    items = []
    for goal in goals:
        total, done = await compute_goal_progress(session, goal.id)
        items.append(
            schemas.GoalOut(
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
        )
    return {"items": items}
