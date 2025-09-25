from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime


class TokenData(BaseModel):
    user_id: UUID


class GoalBookStatus(str):
    pass


class BookBase(BaseModel):
    isbn13: str
    title: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    pubyear: Optional[int] = None
    ndc: Optional[str] = None
    ndlc: Optional[str] = None


class BookOut(BookBase):
    reason: Optional[str] = None


class GoalBookOut(BaseModel):
    book: BookOut
    status: str
    position: int
    completed_at: Optional[datetime]


class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None


class GoalCreate(GoalBase):
    recommended_isbns: List[str] = Field(default_factory=list)


class GoalOut(GoalBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    archived: bool
    progress: float
    total_books: int
    done_books: int


class GoalDetailOut(GoalOut):
    books: List[GoalBookOut]


class GoalProgressResponse(BaseModel):
    ok: bool = True
    progress: float
    total_books: int
    done_books: int


class GoalArchivePayload(BaseModel):
    archived: bool


class GoalBookStatusUpdate(BaseModel):
    status: str = Field(pattern="^(unread|reading|done)$")
