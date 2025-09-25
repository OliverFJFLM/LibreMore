from typing import List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..ext.calil import check_availability
from ..ext.opac_link import opac_isbn_url

router = APIRouter(tags=["availability"])


class AvailabilityIn(BaseModel):
    isbns: List[str] = Field(min_length=1)
    city: str


@router.post("/availability")
async def availability(payload: AvailabilityIn):
    rows = await check_availability(payload.isbns, payload.city)
    for row in rows:
        row["opacUrl"] = opac_isbn_url(row["systemid"], row["isbn13"])
    return rows
