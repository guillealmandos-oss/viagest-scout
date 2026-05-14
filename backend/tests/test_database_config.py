from app.core.database import normalize_database_url


def test_normalize_database_url_keeps_sqlite_untouched():
    assert normalize_database_url("sqlite:///./travel_strategy.db") == "sqlite:///./travel_strategy.db"


def test_normalize_database_url_converts_postgres_scheme():
    assert (
        normalize_database_url("postgres://user:pass@host:5432/dbname")
        == "postgresql+psycopg://user:pass@host:5432/dbname"
    )


def test_normalize_database_url_converts_postgresql_scheme():
    assert (
        normalize_database_url("postgresql://user:pass@host:5432/dbname")
        == "postgresql+psycopg://user:pass@host:5432/dbname"
    )
