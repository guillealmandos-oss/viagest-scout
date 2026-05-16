from app.core.airline_codes import filter_airline_codes, is_placeholder_airline_code
from app.services.providers.duffel import DuffelFlightProvider
from tests.test_duffel_provider import sample_duffel_offer


def test_placeholder_airline_codes():
    assert is_placeholder_airline_code("ZZ")
    assert is_placeholder_airline_code("n/a")
    assert not is_placeholder_airline_code("TP")


def test_filter_airline_codes_drops_zz():
    assert filter_airline_codes(["ZZ", "TP", "ZZ"]) == ["TP"]


def test_duffel_miles_hint_omits_zz_when_only_placeholder():
    offer = sample_duffel_offer()
    offer["owner"] = {"name": "Duffel Airways", "iata_code": "ZZ"}
    for segment in offer["slices"][0]["segments"]:
        segment["marketing_carrier"] = {"iata_code": "ZZ", "name": "Duffel Airways"}
        segment["operating_carrier"] = {"iata_code": "ZZ", "name": "Duffel Airways"}

    mapped = DuffelFlightProvider()._map_offer(offer)

    assert mapped["cash_miles_hint_key"] == "provider.duffel.miles_hint.owner"
    assert mapped["cash_miles_hint_params"] == {"owner": "Duffel Airways"}
