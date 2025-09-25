import logging
import re
from typing import Dict, List
from urllib.parse import urlencode

import feedparser
import httpx

from ..config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def _to_isbn13(isbn: str) -> str | None:
    if not isbn:
        return None
    digits = re.sub(r"[^0-9Xx]", "", isbn)
    return digits if len(digits) in (10, 13) else None


async def _fetch_feed(url: str) -> feedparser.FeedParserDict | None:
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPError as exc:  # pragma: no cover - log branch
        logger.warning("NDL request failed: %s", exc)
        return None
    return feedparser.parse(response.text)


async def search_ndl_by_query(q: str, limit: int = 20) -> List[Dict]:
    if not q.strip():
        return []

    params = {"q": q, "cnt": limit}
    url = f"{settings.ndl_api_base}?{urlencode(params)}"
    feed = await _fetch_feed(url)
    if feed is None:
        return []

    items: List[Dict] = []
    for entry in feed.entries:
        title = entry.get("title")
        author = entry.get("author")
        publisher = entry.get("publisher") or entry.get("dc_publisher")
        date = entry.get("issued") or entry.get("published")
        year = None
        if date:
            match = re.search(r"\d{4}", str(date))
            year = int(match.group(0)) if match else None

        isbns: list[str] = []
        for key, value in entry.items():
            if "isbn" in key.lower():
                if isinstance(value, list):
                    isbns.extend(value)
                else:
                    isbns.append(value)

        isbn13 = None
        for raw in isbns:
            candidate = _to_isbn13(str(raw))
            if candidate and len(candidate) == 13:
                isbn13 = candidate
                break

        if not isbn13:
            continue

        items.append(
            {
                "isbn13": isbn13,
                "title": title,
                "author": author,
                "publisher": publisher,
                "pubyear": year,
                "ndc": None,
                "ndlc": None,
            }
        )
    return items
