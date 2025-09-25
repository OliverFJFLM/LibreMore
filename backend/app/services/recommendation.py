from __future__ import annotations

from typing import Any, Dict, List

from ..ext.ndl import search_ndl_by_query
from ..ext.cinii import search_cinii_by_title


async def generate_recommendations(purpose: str, limit: int = 12) -> List[Dict[str, Any]]:
    ndl_results = await search_ndl_by_query(purpose, limit=30)
    cinii_results = await search_cinii_by_title(purpose, limit=20)

    merged: dict[str, dict[str, Any]] = {}
    for book in ndl_results + cinii_results:
        isbn = book.get("isbn13")
        if not isbn:
            continue
        if isbn not in merged:
            merged[isbn] = book

    final = []
    for idx, book in enumerate(list(merged.values())[:limit]):
        final.append(
            {
                "isbn13": book.get("isbn13"),
                "title": book.get("title"),
                "author": book.get("author"),
                "publisher": book.get("publisher"),
                "pubyear": book.get("pubyear"),
                "reason": "目的との主題一致（MVPルール）",
                "ndc": book.get("ndc"),
                "ndlc": book.get("ndlc"),
            }
        )
    return final
