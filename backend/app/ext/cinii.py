import re
from typing import Dict, List
from urllib.parse import urlencode

import feedparser
import httpx

from ..config import get_settings

settings = get_settings()


def _normalize_isbn(value: str) -> str | None:
    digits = re.sub(r"[^0-9Xx]", "", value)
    return digits if len(digits) in (10, 13) else None


async def search_cinii_by_title(q: str, limit: int = 20) -> List[Dict]:
    params = {"title": q, "count": limit, "format": "rss"}
    url = f"{settings.cinii_base}?{urlencode(params)}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
    items = []
    for entry in feed.entries:
        title = entry.get("title")
        author = entry.get("author")
        summary = entry.get("summary", "")
        match = re.search(r"ISBN[:\s]*([0-9Xx\-]+)", summary)
        isbn13 = None
        if match:
            candidate = _normalize_isbn(match.group(1))
            if candidate and len(candidate) == 13:
                isbn13 = candidate
        if not isbn13:
            continue
        items.append(
            {
                "isbn13": isbn13,
                "title": title,
                "author": author,
                "publisher": None,
                "pubyear": None,
                "ndc": None,
                "ndlc": None,
            }
        )
    return items
