# API Contract

## `POST /api/v1/searches`

Crea una busqueda completa, consulta proveedor de vuelos, genera estrategias y persiste el resultado.

### Request

```json
{
  "user": {
    "email": "traveler@example.com",
    "display_name": "Ana"
  },
  "traveler_profile": {
    "nationality": "UY",
    "residence_country": "UY",
    "checked_bag_required": true,
    "max_stops": 2,
    "travel_priority": "experience",
    "stopover_interest": true,
    "risk_tolerance": "medium",
    "valid_visas": ["US"]
  },
  "loyalty_profiles": [
    {
      "program_name": "Smiles",
      "balance": 28000,
      "bank_name": "Santander",
      "transfer_partners": ["Gol", "Air France"]
    }
  ],
  "search": {
    "origin": "MVD",
    "destination": "NRT",
    "departure_date": "2026-06-18",
    "return_date": "2026-06-28",
    "flexible_days": 2,
    "budget_usd": 1200,
    "passengers": 1,
    "cabin_class": "ECONOMY",
    "checked_bag_required": true,
    "stopover_interest": true,
    "preferred_strategy": "experience",
    "notes": "Evitar conexiones que compliquen visa."
  }
}
```

### Response

```json
{
  "search_id": "uuid",
  "provider_name": "duffel",
  "summary": "Encontramos 3 estrategias accionables...",
  "assumptions": [
    {
      "scope": "migration",
      "rule": "Canada transit",
      "confidence": "medium",
      "note": "Canada puede requerir eTA o visa segun nacionalidad."
    }
  ],
  "strategies": [
    {
      "strategy_type": "savings",
      "title": "Estrategia ahorro",
      "recommendation_badge": "Menor costo total con friccion controlada",
      "total_score": 83.5,
      "explanation": "Esta opcion prioriza costo total...",
      "tradeoffs": ["Pagas ..."],
      "opportunity_notes": ["Agregar Lisboa cuesta ..."],
      "score_breakdown": {
        "price": 95,
        "duration": 76
      },
      "itinerary": {
        "id": "offer-id",
        "provider_offer_id": "save-madrid",
        "provider_name": "duffel",
        "title": "Opcion Duffel MVD-NRT",
        "total_price": 954.2,
        "currency": "USD"
      },
      "is_recommended": false
    }
  ],
  "created_at": "2026-05-14T18:00:00Z"
}
```

## `GET /api/v1/searches`

Lista busquedas persistidas recientemente para debugging/manual QA.

## `GET /api/v1/searches/{search_id}`

Recupera una busqueda completa con sus estrategias e itinerarios asociados.

## `POST /api/v1/analytics/events`

Captura eventos de producto como:

- `result_viewed`
- `strategy_opened`
- `recommendation_saved`
- `feedback_submitted`

## `GET /api/v1/analytics/summary`

Devuelve el resumen del panel beta:

- total de busquedas
- total de eventos
- estrategias abiertas
- recomendaciones guardadas
- feedback reciente

## `GET /api/v1/analytics/provider-health`

Devuelve salud agregada por proveedor:

- intentos totales
- intentos exitosos
- intentos fallidos
- tasa de éxito
- latencia promedio
- promedio de ofertas por búsqueda
- último error observado
- último `external_request_id` observado
- último `external_correlation_id` observado
