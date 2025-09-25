import asyncio
import hashlib
import json
import os
import random
from typing import Dict, List

import httpx
import redis.asyncio as aioredis

from ..config import get_settings

settings = get_settings()

CALIL_APPKEY = settings.calil_appkey
CALIL_BASE = "https://api.calil.jp"

redis = aioredis.from_url(settings.redis_url) if settings.redis_url else None


async def get_systemids_for_city(city: str) -> List[str]:
    cache_key = f"sysids:{city}"
    if redis:
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)
    systemids = ["MiyazakiSys-001", "MiyazakiSys-002"]
    if redis:
        await redis.set(cache_key, json.dumps(systemids), ex=60 * 60 * 24 * 30)
    return systemids


async def check_availability(isbns: List[str], city: str) -> List[Dict]:
    digest = hashlib.sha1((",".join(sorted(isbns)) + city).encode()).hexdigest()
    cache_key = f"avail:{digest}"
    if redis:
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)

    systemids = await get_systemids_for_city(city)
    params = {
        "appkey": CALIL_APPKEY,
        "isbn": ",".join(isbns),
        "systemid": ",".join(systemids),
        "format": "json",
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(f"{CALIL_BASE}/check", params=params)
        resp.raise_for_status()
        data = resp.json()
        session = data.get("session")
        cont = data.get("continue", 0)
        while cont == 1:
            await asyncio.sleep(0.8 + random.random() * 0.6)
            poll = await client.get(
                f"{CALIL_BASE}/check",
                params={"appkey": CALIL_APPKEY, "session": session, "format": "json"},
            )
            poll.raise_for_status()
            data = poll.json()
            cont = data.get("continue", 0)

    # Placeholder transformation for MVP
    results: List[Dict] = []
    for systemid in systemids:
        for isbn in isbns:
            results.append({"isbn13": isbn, "systemid": systemid, "status": "在架"})

    if redis:
        await redis.set(cache_key, json.dumps(results), ex=60 * 15)
    return results
