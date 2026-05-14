from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.models.base import Base


settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, future=True, connect_args=connect_args)
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
    if "searches" not in inspector.get_table_names():
        return

    search_columns = {column["name"] for column in inspector.get_columns("searches")}
    with engine.begin() as connection:
        if "content_locale" not in search_columns:
            connection.execute(text("ALTER TABLE searches ADD COLUMN content_locale VARCHAR(8)"))
            connection.execute(text("UPDATE searches SET content_locale = 'es' WHERE content_locale IS NULL"))
