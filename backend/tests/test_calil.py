import os

import pytest

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/library")
os.environ.setdefault("JWT_SECRET", "test-secret")

from app.ext import calil


@pytest.mark.asyncio
async def test_check_availability_without_appkey(monkeypatch):
    monkeypatch.setattr(calil, "CALIL_APPKEY", None)
    rows = await calil.check_availability(["9781234567890"], "宮崎市")
    assert rows
    assert all(row["status"] == calil.DEFAULT_STATUS for row in rows)
    assert {row["systemid"] for row in rows} == {"MiyazakiSys-001", "MiyazakiSys-002"}
