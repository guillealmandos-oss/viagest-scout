# Viagest Scout MVP

Implementacion inicial de `Viagest Scout`, la app de descubrimiento y estrategia inteligente de vuelos con IA dentro del ecosistema Viagest.

## Estructura

- `frontend/`: web app en `Next.js` con intake inteligente, comparacion de estrategias y captura de feedback.
- `backend/`: API en `FastAPI` con persistencia local, proveedor de vuelos desacoplado, normalizacion, scoring, reglas migratorias y analytics.
- `docs/`: contrato API, decisiones tecnicas y wireframes low-fi del flujo principal.

## Stack elegido

- Frontend: `Next.js 16` + `React 19` + `Tailwind 4`
- Backend: `FastAPI` + `SQLAlchemy`
- Persistencia local para desarrollo: `SQLite`
- Path de evolucion: `PostgreSQL` via `DATABASE_URL`
- LLM: OpenAI opcional, con fallback templated si no hay clave
- Proveedor de vuelos: adaptadores `Duffel`, `Amadeus` y `demo`, seleccionables por entorno
- Orquestacion multi-provider: `FLIGHT_PROVIDERS=duffel,amadeus` permite buscar en varios proveedores y deduplicar resultados

## Como correrlo

### 1. Backend

```powershell
cd "c:\Users\galma\Downloads\mao sistema gestio\travel-ai-strategist\backend"
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### 2. Frontend

```powershell
cd "c:\Users\galma\Downloads\mao sistema gestio\travel-ai-strategist\frontend"
Copy-Item .env.example .env.local
npm run dev
```

### 3. Build de produccion opcional

```powershell
cd "c:\Users\galma\Downloads\mao sistema gestio\travel-ai-strategist\frontend"
npm run build
npm start -- --port 3001
```

Si vas a abrir el frontend en otro puerto distinto de `3000`, agrega ese origen en `backend/.env` dentro de `ALLOWED_ORIGINS`.

## Modo bilingue

- La web soporta `es` y `en`.
- El root detecta idioma del navegador y redirige a `/{locale}`.
- Tambien hay selector manual de idioma en el header.
- Rutas principales:
  - `http://localhost:3000/es`
  - `http://localhost:3000/en`
- Resultados de busqueda:
  - `http://localhost:3000/es/search/<search_id>`
  - `http://localhost:3000/en/search/<search_id>`

## Idioma en API

- El frontend envia `X-Locale` y `Accept-Language` al backend.
- El backend genera copy nuevo en el idioma activo.
- Una misma busqueda persistida puede leerse luego en `es` o `en` sin recrearla.
- Si no mandas locale explicito, el backend hace fallback a `es`.

Ejemplo:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/v1/searches/<search_id>" `
  -Headers @{ "X-Locale" = "en" }
```

## Configuracion de proveedores

### Solo Duffel

```env
FLIGHT_PROVIDER=duffel
FLIGHT_PROVIDERS=duffel
DUFFEL_API_TOKEN=duffel_test_...
```

### Duffel + Amadeus

```env
FLIGHT_PROVIDER=duffel
FLIGHT_PROVIDERS=duffel,amadeus
DUFFEL_API_TOKEN=duffel_test_...
AMADEUS_API_KEY=...
AMADEUS_API_SECRET=...
```

### Demo explicito

```env
FLIGHT_PROVIDER=demo
FLIGHT_PROVIDERS=demo
```

Si definis `FLIGHT_PROVIDERS`, el backend intenta esos proveedores en paralelo, mergea resultados y elimina duplicados cercanos.

### Timeouts por proveedor

```env
PROVIDER_TIMEOUTS=duffel:30,amadeus:25,demo:5
```

Cada valor se interpreta en segundos. Si un proveedor no tiene timeout configurado, el backend usa `20s`.

## Deploy recomendado

La opcion recomendada para publicarlo completo es `Railway`:

- `backend/` como servicio `FastAPI`
- `frontend/` como servicio `Next.js`
- `PostgreSQL` administrado por Railway

Guia paso a paso:

- `docs/deploy-railway.md`

## Flujo actual

1. El usuario completa contexto de viaje, perfil migratorio y loyalty.
2. El backend consulta uno o varios proveedores segun configuracion.
3. Normaliza las ofertas a un modelo comun.
4. Hace merge y dedupe entre ofertas equivalentes.
5. Aplica scoring, reglas de riesgo y notas migratorias.
6. Selecciona 3 estrategias: `ahorro`, `experiencia`, `millas`.
7. Devuelve explicacion, tradeoffs y oportunidades.
8. El frontend permite expandir detalle, guardar recomendacion y enviar feedback.

## Validacion rapida

1. Levanta backend en `8000`.
2. Levanta frontend en `3000` o `3001`.
3. Abre `/en` y `/es` para confirmar textos localizados.
4. Crea una busqueda en ingles.
5. Abre el mismo `search_id` en `/en/search/...` y `/es/search/...`.
6. Confirma que cambian al menos `summary`, `title` y `recommendation_badge`.

## Notas de implementacion

- No se mezclo este MVP con la app legacy del workspace.
- `Duffel` es ahora el proveedor por defecto. Si falla, el backend devuelve error y no cambia de proveedor silenciosamente.
- Si definis `FLIGHT_PROVIDERS`, el backend consulta varios proveedores en paralelo, mergea resultados y elimina duplicados cercanos.
- `demo` sigue existiendo solo como modo explicito para pruebas internas si se define `FLIGHT_PROVIDER=demo`.
- `Duffel` usa `Duffel-Version: v2` y el endpoint `POST /air/offer_requests`, ya preparado en el adaptador.
- La integracion `Amadeus` se mantiene disponible, pero el self-service actual no esta siendo el camino principal.
- Las reglas migratorias son deliberadamente conservadoras y parciales; el API devuelve supuestos para explicitar cobertura.
- El backend ahora persiste `content_locale` y re-renderiza respuestas localizadas para `es/en`.
- La guia de arquitectura multi-provider esta en `docs/multi-provider-architecture.md`.
