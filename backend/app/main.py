from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analytics_router, searches_router
from app.core.config import get_settings
from app.core.database import init_db


settings = get_settings()
init_db()

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(searches_router)
app.include_router(analytics_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "environment": settings.app_env, "provider": settings.flight_provider}
