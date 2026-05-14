from __future__ import annotations

from dataclasses import dataclass

from app.core.i18n import message_item
from app.schemas.common import ItineraryOption, RiskFlag, TravelerProfileInput


@dataclass(slots=True)
class MigrationAssessment:
    risk_flags: list[RiskFlag]
    migration_notes: list[str]
    migration_note_items: list[dict]
    assumptions: list[dict]


class MigrationRulesEngine:
    USA_AIRPORTS = {"JFK", "MIA", "ATL", "DFW", "LAX", "ORD"}
    CANADA_AIRPORTS = {"YYZ", "YVR", "YUL"}
    UK_AIRPORTS = {"LHR", "LGW"}

    def assess(self, itinerary: ItineraryOption, traveler: TravelerProfileInput) -> MigrationAssessment:
        flags: list[RiskFlag] = []
        notes: list[str] = []
        note_items: list[dict] = []
        assumptions: list[dict] = []

        valid_visas = {visa.upper() for visa in traveler.valid_visas}
        layover_airports = {layover.airport for layover in itinerary.layovers}

        if layover_airports & self.USA_AIRPORTS:
            assumptions.append(
                {
                    "scope": "migration",
                    "rule": "US sterile transit",
                    "confidence": "high",
                    "rule_key": "migration.assumption.us.rule",
                    "note_key": "migration.assumption.us.note",
                }
            )
            if not {"US", "USA", "B1/B2", "ESTA"} & valid_visas and traveler.nationality != "US":
                flags.append(
                    RiskFlag(
                        code="us_transit_authorization",
                        severity="high",
                        message="La conexion via EE.UU. puede requerir visa o ESTA incluso en transito.",
                        message_key="migration.flag.us_transit_authorization",
                    )
                )
                notes.append("Evitar via EE.UU. si no tienes visa o ESTA confirmado.")
                note_items.append(message_item("migration.note.us_avoid"))

        if layover_airports & self.CANADA_AIRPORTS:
            assumptions.append(
                {
                    "scope": "migration",
                    "rule": "Canada transit",
                    "confidence": "medium",
                    "rule_key": "migration.assumption.canada.rule",
                    "note_key": "migration.assumption.canada.note",
                }
            )
            if not {"CANADA", "US", "USA"} & valid_visas and traveler.nationality not in {"CA", "US"}:
                flags.append(
                    RiskFlag(
                        code="canada_transit_review",
                        severity="medium",
                        message="La conexion via Canada requiere revisar eTA o visa antes de emitir.",
                        message_key="migration.flag.canada_transit_review",
                    )
                )
                notes.append("Conexion via Canada: validar eTA o visa antes de avanzar.")
                note_items.append(message_item("migration.note.canada_review"))

        if layover_airports & self.UK_AIRPORTS:
            assumptions.append(
                {
                    "scope": "migration",
                    "rule": "UK airside transit",
                    "confidence": "low",
                    "rule_key": "migration.assumption.uk.rule",
                    "note_key": "migration.assumption.uk.note",
                }
            )
            if not {"UK", "GBR"} & valid_visas and traveler.nationality not in {"GB", "IE"}:
                flags.append(
                    RiskFlag(
                        code="uk_transit_review",
                        severity="medium",
                        message="La conexion via Reino Unido necesita validacion de visa de transito.",
                        message_key="migration.flag.uk_transit_review",
                    )
                )
                notes.append("Via Reino Unido: revisar si aplica visa de transito airside/landside.")
                note_items.append(message_item("migration.note.uk_review"))

        return MigrationAssessment(
            risk_flags=flags,
            migration_notes=notes,
            migration_note_items=note_items,
            assumptions=assumptions,
        )
