from __future__ import annotations

from datetime import datetime, time, timedelta
from uuid import uuid4

from app.schemas.common import CabinClass, SearchRequestInput
from app.services.providers.base import BaseFlightProvider


class DemoFlightProvider(BaseFlightProvider):
    provider_name = "demo"

    async def search_offers(self, search_input: SearchRequestInput) -> list[dict]:
        outbound_date = search_input.departure_date
        return_date = search_input.return_date or search_input.departure_date + timedelta(days=10)

        def merge_rt(**kwargs: object) -> tuple[list[dict], list[list[dict]]]:
            out_segs, in_segs = self._round_trip_segments(**kwargs)
            return out_segs + in_segs, [out_segs, in_segs]

        sm_segs, sm_by = merge_rt(
            outbound_date=outbound_date,
            return_date=return_date,
            outbound=[
                self._segment(search_input.origin, "MAD", time(8, 10), 130, "IB", "6040"),
                self._segment("MAD", search_input.destination, time(13, 15), 790, "IB", "6217"),
            ],
            inbound=[
                self._segment(search_input.destination, "MAD", time(11, 5), 780, "IB", "6216"),
                self._segment("MAD", search_input.origin, time(22, 25), 135, "IB", "6041"),
            ],
        )
        lis_segs, lis_by = merge_rt(
            outbound_date=outbound_date,
            return_date=return_date,
            outbound=[
                self._segment(search_input.origin, "LIS", time(7, 45), 125, "TP", "118"),
                self._segment("LIS", search_input.destination, time(13, 5), 840, "TP", "320"),
            ],
            inbound=[
                self._segment(search_input.destination, "LIS", time(9, 25), 835, "TP", "319"),
                self._segment("LIS", search_input.origin, time(19, 0), 125, "TP", "117"),
            ],
            outbound_layovers=[30 * 60],
            inbound_layovers=[3 * 60 + 15],
        )
        ist_segs, ist_by = merge_rt(
            outbound_date=outbound_date,
            return_date=return_date,
            outbound=[
                self._segment(search_input.origin, "IST", time(6, 20), 1000, "TK", "16", cabin_class="ECONOMY"),
                self._segment("IST", search_input.destination, time(1, 10), 610, "TK", "50", cabin_class="BUSINESS"),
            ],
            inbound=[
                self._segment(search_input.destination, "IST", time(15, 45), 600, "TK", "51", cabin_class="BUSINESS"),
                self._segment("IST", search_input.origin, time(23, 50), 995, "TK", "15", cabin_class="ECONOMY"),
            ],
            outbound_layovers=[2 * 60 + 10],
            inbound_layovers=[4 * 60],
        )
        yyz_segs, yyz_by = merge_rt(
            outbound_date=outbound_date,
            return_date=return_date,
            outbound=[
                self._segment(search_input.origin, "YYZ", time(8, 55), 690, "AC", "883"),
                self._segment("YYZ", search_input.destination, time(21, 10), 630, "WS", "12"),
            ],
            inbound=[
                self._segment(search_input.destination, "YYZ", time(8, 0), 625, "WS", "11"),
                self._segment("YYZ", search_input.origin, time(18, 20), 685, "AC", "882"),
            ],
            outbound_layovers=[55],
            inbound_layovers=[70],
        )
        dir_segs, dir_by = merge_rt(
            outbound_date=outbound_date,
            return_date=return_date,
            outbound=[
                self._segment(search_input.origin, search_input.destination, time(9, 30), 860, "LA", "800"),
            ],
            inbound=[
                self._segment(search_input.destination, search_input.origin, time(17, 45), 855, "LA", "801"),
            ],
        )

        return [
            self._build_offer(
                offer_code="save-madrid",
                title="Ahorro via Madrid",
                title_key="provider.demo.title.save_madrid",
                total_price=842,
                baggage_included=True,
                flexibility_code="semi",
                self_transfer=False,
                segments=sm_segs,
                segments_by_slice=sm_by,
                cash_miles_hint="Guardar millas para un tramo largo da mejor valor.",
                cash_miles_hint_key="provider.demo.hint.save_madrid",
            ),
            self._build_offer(
                offer_code="stopover-lisbon",
                title="Experiencia con stopover en Lisboa",
                title_key="provider.demo.title.stopover_lisbon",
                total_price=889,
                baggage_included=True,
                flexibility_code="total",
                self_transfer=False,
                segments=lis_segs,
                segments_by_slice=lis_by,
                cash_miles_hint="El stopover agrega valor por un delta de costo bajo.",
                cash_miles_hint_key="provider.demo.hint.stopover_lisbon",
            ),
            self._build_offer(
                offer_code="miles-istanbul",
                title="Maximizar millas en el tramo largo",
                title_key="provider.demo.title.miles_istanbul",
                total_price=1298,
                baggage_included=True,
                flexibility_code="total",
                self_transfer=False,
                segments=ist_segs,
                segments_by_slice=ist_by,
                cash_miles_hint="Tiene mejor valor por punto si canjeas solo la cabina premium.",
                cash_miles_hint_key="provider.demo.hint.miles_istanbul",
            ),
            self._build_offer(
                offer_code="risk-toronto",
                title="Precio bajo pero con conexion riesgosa",
                title_key="provider.demo.title.risk_toronto",
                total_price=801,
                baggage_included=False,
                flexibility_code="basic",
                self_transfer=True,
                segments=yyz_segs,
                segments_by_slice=yyz_by,
                cash_miles_hint="Solo conviene si aceptas visa y self-transfer.",
                cash_miles_hint_key="provider.demo.hint.risk_toronto",
            ),
            self._build_offer(
                offer_code="comfort-direct",
                title="Comodidad y menor friccion",
                title_key="provider.demo.title.comfort_direct",
                total_price=1435,
                baggage_included=True,
                flexibility_code="total",
                self_transfer=False,
                segments=dir_segs,
                segments_by_slice=dir_by,
                cash_miles_hint="Conviene si priorizas tiempo total y cambios simples.",
                cash_miles_hint_key="provider.demo.hint.comfort_direct",
            ),
        ]

    def _round_trip_segments(
        self,
        *,
        outbound_date,
        return_date,
        outbound: list[dict],
        inbound: list[dict],
        outbound_layovers: list[int] | None = None,
        inbound_layovers: list[int] | None = None,
    ) -> tuple[list[dict], list[dict]]:
        outbound_segments = self._place_segments(outbound_date, outbound, outbound_layovers or [])
        inbound_segments = self._place_segments(return_date, inbound, inbound_layovers or [])
        return outbound_segments, inbound_segments

    def _place_segments(self, travel_date, segments: list[dict], layovers: list[int]) -> list[dict]:
        placed: list[dict] = []
        cursor = datetime.combine(travel_date, time(0, 0))
        for index, segment in enumerate(segments):
            departure_at = datetime.combine(travel_date, segment["departure_time"])
            if index > 0 and index - 1 < len(layovers):
                departure_at = cursor + timedelta(minutes=layovers[index - 1])
            elif index > 0:
                while departure_at <= cursor:
                    departure_at += timedelta(days=1)
            arrival_at = departure_at + timedelta(minutes=segment["duration_minutes"])
            cursor = arrival_at
            segment_payload = {key: value for key, value in segment.items() if key != "departure_time"}
            placed.append(
                {
                    **segment_payload,
                    "departure_at": departure_at.isoformat(),
                    "arrival_at": arrival_at.isoformat(),
                }
            )
        return placed

    def _segment(
        self,
        origin: str,
        destination: str,
        departure_time: time,
        duration_minutes: int,
        airline: str,
        flight_number: str,
        cabin_class: CabinClass = "ECONOMY",
    ) -> dict:
        return {
            "origin": origin,
            "destination": destination,
            "departure_time": departure_time,
            "duration_minutes": duration_minutes,
            "airline": airline,
            "flight_number": flight_number,
            "cabin_class": cabin_class,
        }

    def _build_offer(
        self,
        *,
        offer_code: str,
        title: str,
        title_key: str,
        total_price: float,
        baggage_included: bool,
        flexibility_code: str,
        self_transfer: bool,
        segments: list[dict],
        segments_by_slice: list[list[dict]],
        cash_miles_hint: str,
        cash_miles_hint_key: str,
    ) -> dict:
        flexibility_label_map = {
            "total": "Flexible total",
            "semi": "Semi flexible",
            "basic": "Basica",
        }
        return {
            "id": str(uuid4()),
            "offer_code": offer_code,
            "provider_name": self.provider_name,
            "title": title,
            "title_key": title_key,
            "total_price": total_price,
            "currency": "USD",
            "baggage_included": baggage_included,
            "flexibility_label": flexibility_label_map[flexibility_code],
            "flexibility_code": flexibility_code,
            "self_transfer": self_transfer,
            "segments": segments,
            "segments_by_slice": segments_by_slice,
            "cash_miles_hint": cash_miles_hint,
            "cash_miles_hint_key": cash_miles_hint_key,
        }
