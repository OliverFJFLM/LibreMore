from typing import List

from fastapi import APIRouter

from ..schemas import BookOut
from ..services.recommendation import generate_recommendations

router = APIRouter(tags=["recommend"])


@router.post("/recommend", response_model=List[BookOut])
async def recommend(payload: dict) -> List[BookOut]:
    purpose = str(payload.get("purpose", "")).strip()
    if not purpose:
        return []
    books = await generate_recommendations(purpose)
    return [BookOut(**book) for book in books]
