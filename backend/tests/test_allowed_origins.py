from app.core.config import Settings


def test_allowed_origins_comma_separated() -> None:
    s = Settings(allowed_origins="https://a.test,http://localhost:3000")
    assert s.allowed_origins == ["https://a.test", "http://localhost:3000"]


def test_allowed_origins_json_array() -> None:
    s = Settings(
        allowed_origins='["https://a.test","http://localhost:3000"]',
    )
    assert s.allowed_origins == ["https://a.test", "http://localhost:3000"]


def test_allowed_origins_strips_outer_quotes_and_trailing_slash() -> None:
    s = Settings(allowed_origins='"https://a.test/,http://localhost:3000"')
    assert s.allowed_origins == ["https://a.test", "http://localhost:3000"]


def test_allowed_origins_json_with_inner_quote_noise_still_parses() -> None:
    s = Settings(
        allowed_origins='["https://a.test", "http://localhost:3000"]',
    )
    assert s.allowed_origins == ["https://a.test", "http://localhost:3000"]


def test_frontend_origin_merged_into_allowed_origins() -> None:
    s = Settings(
        allowed_origins="http://localhost:3000",
        frontend_origin="https://app.example.test/",
    )
    assert "http://localhost:3000" in s.allowed_origins
    assert "https://app.example.test" in s.allowed_origins
