import asyncio
from datetime import date

from app.core.i18n import render_message_items, t
from app.schemas.common import LoyaltyProfileInput, SearchRequestInput, TravelerProfileInput
from app.services.migration_rules import MigrationRulesEngine
from app.services.normalizer import FlightOfferNormalizer
from app.services.providers.demo import DemoFlightProvider
from app.services.scoring import ScoringEngine
from app.services.stopover import StopoverAdvisor
from app.services.strategies import StrategyGenerator


def build_itineraries():
    search = SearchRequestInput(
        origin="MVD",
        destination="NRT",
        departure_date=date(2026, 6, 18),
        return_date=date(2026, 6, 28),
        flexible_days=2,
        budget_usd=1200,
        passengers=1,
        cabin_class="ECONOMY",
        checked_bag_required=True,
        stopover_interest=True,
        preferred_strategy="experience",
    )
    provider = DemoFlightProvider()
    normalizer = FlightOfferNormalizer()
    raw_offers = asyncio.run(provider.search_offers(search))
    return search, normalizer.normalize(raw_offers, "es")


def test_migration_engine_flags_us_transit_without_visa():
    _, itineraries = build_itineraries()
    traveler = TravelerProfileInput(
        nationality="UY",
        residence_country="UY",
        checked_bag_required=True,
        max_stops=2,
        travel_priority="balanced",
        stopover_interest=False,
        risk_tolerance="medium",
        valid_visas=[],
    )

    risky_itinerary = next(item for item in itineraries if "YYZ" in item.route_summary)
    assessment = MigrationRulesEngine().assess(risky_itinerary, traveler)

    assert any(flag.code == "canada_transit_review" for flag in assessment.risk_flags)
    assert assessment.migration_notes


def test_stopover_annotation_is_added_for_low_cost_delta():
    _, itineraries = build_itineraries()
    cheapest_price = min(item.total_price for item in itineraries)
    stopover_itinerary = next(item for item in itineraries if "LIS" in item.route_summary)

    notes = StopoverAdvisor().annotate(stopover_itinerary, cheapest_price)

    assert notes
    assert notes[0]["key"] in {"stopover.low_delta", "stopover.experience"}


def test_strategy_generator_returns_three_distinct_strategies():
    search, itineraries = build_itineraries()
    traveler = TravelerProfileInput(
        nationality="UY",
        residence_country="UY",
        checked_bag_required=True,
        max_stops=2,
        travel_priority="experience",
        stopover_interest=True,
        risk_tolerance="medium",
        valid_visas=[],
    )
    loyalty_profiles = [LoyaltyProfileInput(program_name="Smiles", balance=28000, bank_name="Santander")]
    migration_engine = MigrationRulesEngine()
    stopover_advisor = StopoverAdvisor()

    cheapest_price = min(item.total_price for item in itineraries)
    for itinerary in itineraries:
        migration = migration_engine.assess(itinerary, traveler)
        itinerary.risk_flags.extend(migration.risk_flags)
        itinerary.raw_payload["migration_note_items"] = migration.migration_note_items
        itinerary.migration_notes = render_message_items("es", migration.migration_note_items, fallback=migration.migration_notes)
        opportunity_items = stopover_advisor.annotate(itinerary, cheapest_price)
        itinerary.raw_payload["opportunity_note_items"] = opportunity_items
        itinerary.opportunity_notes = render_message_items("es", opportunity_items)
        for flag in itinerary.risk_flags:
            if flag.message_key:
                flag.message = t("es", flag.message_key, **flag.message_params)

    scored = ScoringEngine().score_itineraries(itineraries, search, traveler, loyalty_profiles)
    strategies = StrategyGenerator().generate(scored, search)

    assert len(strategies) == 3
    assert {strategy["strategy_type"] for strategy in strategies} == {"savings", "experience", "miles"}
    assert all(strategy["title_key"].startswith("strategy.title.") for strategy in strategies)
