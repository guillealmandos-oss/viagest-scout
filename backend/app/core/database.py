from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.models.base import Base


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


settings = get_settings()
resolved_database_url = normalize_database_url(settings.database_url)

connect_args = {"check_same_thread": False} if resolved_database_url.startswith("sqlite") else {}
engine = create_engine(resolved_database_url, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _run_lightweight_migrations()


def _run_lightweight_migrations() -> None:
    inspector = inspect(engine)
    dialect = engine.dialect.name

    if "searches" in inspector.get_table_names():
        search_columns = {column["name"] for column in inspector.get_columns("searches")}
        with engine.begin() as connection:
            if "content_locale" not in search_columns:
                connection.execute(text("ALTER TABLE searches ADD COLUMN content_locale VARCHAR(8)"))
                connection.execute(text("UPDATE searches SET content_locale = 'es' WHERE content_locale IS NULL"))

    # Postgres enforces VARCHAR length; guardamos itinerary.title aquí (suele ser >>32 chars).
    if dialect == "postgresql" and "itineraries" in inspector.get_table_names():
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE itineraries ALTER COLUMN itinerary_type TYPE VARCHAR(512)"))
