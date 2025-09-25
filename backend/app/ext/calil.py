import asyncio
import hashlib
import json
import logging
import random
from typing import Dict, List

import httpx
import redis.asyncio as aioredis

from ..config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

CALIL_APPKEY = settings.calil_appkey
CALIL_BASE = "https://api.calil.jp"
DEFAULT_STATUS = "照会中"

redis = aioredis.from_url(settings.redis_url) if settings.redis_url else None

POSITIVE_KEYWORDS = ("在庫", "蔵書", "利用可", "提供")
LOAN_KEYWORDS = ("貸出", "貸し出し", "貸出中")
RESERVE_KEYWORDS = ("予約",)
STATUS_TRANSLATIONS = {
    "OK": "在架",
    "NG": "蔵書なし",
    "Cache": "在架(キャッシュ)",
    "Running": DEFAULT_STATUS,
}


def _has_valid_appkey() -> bool:
    if not CALIL_APPKEY:
        return False
    return CALIL_APPKEY.strip().lower() not in {"", "replace_me"}


def _fallback_rows(systemids: List[str], isbns: List[str], status: str = DEFAULT_STATUS) -> List[Dict]:
    return [
        {"isbn13": isbn, "systemid": systemid, "status": status}
        for systemid in systemids
        for isbn in isbns
    ]


def _interpret_status(payload: Dict | None) -> str:
    if not payload:
        return DEFAULT_STATUS
    status_code = payload.get("status")
    status = STATUS_TRANSLATIONS.get(status_code, DEFAULT_STATUS if status_code is None else str(status_code))

    libkey = payload.get("libkey") or {}
    if isinstance(libkey, dict) and libkey:
        values = [str(value) for value in libkey.values()]
        if any(any(keyword in value for keyword in POSITIVE_KEYWORDS) for value in values):
            status = "在架"
        elif any(any(keyword in value for keyword in LOAN_KEYWORDS) for value in values):
            status = "貸出中"
        elif any(any(keyword in value for keyword in RESERVE_KEYWORDS) for value in values):
            status = "予約受付中"
    return status


async def get_systemids_for_city(city: str) -> List[str]:
    cache_key = f"sysids:{city}"
    if redis:
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)

    # TODO: Calilライブラリ一覧APIへの接続を実装する。
    systemids = ["MiyazakiSys-001", "MiyazakiSys-002"]
    if redis:
        await redis.set(cache_key, json.dumps(systemids), ex=60 * 60 * 24 * 30)
    if not _has_valid_appkey():  # pragma: no cover - log branch
        logger.info("Using static systemid list for city '%s'", city)
    return systemids


async def _request_check(client: httpx.AsyncClient, params: Dict) -> Dict:
    response = await client.get(f"{CALIL_BASE}/check", params=params)
    response.raise_for_status()
    return response.json()


async def check_availability(isbns: List[str], city: str) -> List[Dict]:
    digest = hashlib.sha1((",".join(sorted(isbns)) + city).encode()).hexdigest()
    cache_key = f"avail:{digest}"
    if redis:
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)

    systemids = await get_systemids_for_city(city)

    if not _has_valid_appkey():
        results = _fallback_rows(systemids, isbns)
        if redis:
            await redis.set(cache_key, json.dumps(results), ex=60 * 5)
        return results

    params = {
        "appkey": CALIL_APPKEY,
        "isbn": ",".join(isbns),
        "systemid": ",".join(systemids),
        "format": "json",
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            data = await _request_check(client, params)
            session = data.get("session")
            cont = data.get("continue", 0)
            while cont == 1:
                await asyncio.sleep(0.8 + random.random() * 0.6)
                data = await _request_check(client, {"appkey": CALIL_APPKEY, "session": session, "format": "json"})
                cont = data.get("continue", 0)
    except httpx.HTTPError as exc:  # pragma: no cover - log branch
        logger.warning("Calil availability request failed: %s", exc)
        results = _fallback_rows(systemids, isbns)
        if redis:
            await redis.set(cache_key, json.dumps(results), ex=60 * 5)
        return results

    books_payload = data.get("books") or {}
    results: List[Dict] = []
    for isbn in isbns:
        systems = books_payload.get(isbn) if isinstance(books_payload, dict) else None
        for systemid in systemids:
            entry = None
            if isinstance(systems, dict):
                entry = systems.get(systemid)
            status = _interpret_status(entry if isinstance(entry, dict) else None)
            results.append({"isbn13": isbn, "systemid": systemid, "status": status})

    if redis:
        await redis.set(cache_key, json.dumps(results), ex=60 * 15)
    return results
