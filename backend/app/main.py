import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analytics_router, searches_router
from app.core.config import get_settings
from app.core.database import init_db


settings = get_settings()
init_db()

_startup_logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _startup_logger.info("CORS allow_origins=%s", list(settings.allowed_origins))
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
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
