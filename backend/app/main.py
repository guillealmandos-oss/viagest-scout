import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analytics_router, searches_router
from app.core.config import get_settings
from app.core.database import init_db
from app.core.flight_providers_config import flight_inventory_status


settings = get_settings()
init_db()

_startup_logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    inventory = flight_inventory_status()
    _startup_logger.info("CORS allow_origins=%s", list(settings.allowed_origins))
    _startup_logger.info(
        "Flight providers active=%s skipped=%s test_inventory=%s",
        inventory["active_providers"],
        inventory["skipped_providers"],
        inventory["uses_test_inventory"],
    )
    if not inventory["active_providers"]:
        _startup_logger.warning(
            "No live flight providers enabled. Configure Amadeus production or Duffel live token."
        )
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
    inventory = flight_inventory_status()
    return {
        "status": "ok",
        "environment": settings.app_env,
        "provider": settings.flight_provider,
        "flight_providers": inventory,
    }
