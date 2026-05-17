from app.core.i18n import t
from app.services.provider_errors import explain_provider_error, provider_error_item


def test_provider_error_item_maps_duffel_401():
    item = provider_error_item("duffel", "Client error '401 Unauthorized' for url 'https://api.duffel.com/air/offer_requests'")
    assert item["key"] == "provider.error.duffel.unauthorized"


def test_explain_provider_error_renders_spanish_duffel_unauthorized():
    message = explain_provider_error(
        "es",
        "duffel",
        provider_error_item("duffel", "401 Unauthorized"),
    )
    assert message is not None
    assert "401" in message
    assert "Duffel" in message
    assert "duffel_test" not in message.lower() or "live" in message.lower()


def test_explain_provider_error_renders_english_from_stored_detail():
    detail = provider_error_item("duffel", RuntimeError("Duffel token is missing. Set DUFFEL_API_TOKEN to enable live search."))
    message = explain_provider_error("en", "duffel", detail)
    assert message == t("en", "provider.error.duffel.missing_token")
