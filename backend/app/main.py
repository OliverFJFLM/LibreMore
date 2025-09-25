from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import auth, availability, goals, mypage, recommend

settings = get_settings()

app = FastAPI(title="LibreMore API")

origins = [origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(recommend.router)
app.include_router(availability.router)
app.include_router(goals.router)
app.include_router(mypage.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
