# Deploy En Railway

Esta app se despliega mejor en Railway como dos servicios y una base de datos:

- `frontend/` como servicio `Next.js`
- `backend/` como servicio `FastAPI`
- `PostgreSQL` administrado por Railway

## Arquitectura recomendada

1. Crear un proyecto nuevo en Railway.
2. Agregar una base `PostgreSQL`.
3. Crear un servicio desde `backend/`.
4. Crear otro servicio desde `frontend/`.
5. Conectar el frontend al dominio publico del backend.

## 1. Base de datos

En Railway:

- `New` -> `Database` -> `PostgreSQL`
- copiar la variable `DATABASE_URL`

El backend ya soporta:

- `sqlite:///...` para local
- `postgres://...` o `postgresql://...` para Railway

Internamente se normaliza a `postgresql+psycopg://...`.

## 2. Backend

Crear un servicio apuntando a `backend/`.

### Root Directory

`backend`

### Build Command

Railway deberia detectarlo solo con `requirements.txt`.

### Start Command

Si detecta `Procfile`, no hace falta tocar nada. Si queres dejarlo explicito:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Variables sugeridas

```env
APP_NAME=Viagest Scout API
APP_ENV=production
DATABASE_URL=${{Postgres.DATABASE_URL}}
FLIGHT_PROVIDER=amadeus
FLIGHT_PROVIDERS=amadeus
ALLOW_DUFFEL_TEST=false
PROVIDER_TIMEOUTS=amadeus:25,duffel:30
DEFAULT_CURRENCY=USD
ALLOWED_ORIGINS=http://localhost:3000,https://<frontend-domain>.up.railway.app,https://scout.viagest.app
# Alternativa: solo agregar el dominio custom sin reescribir ALLOWED_ORIGINS:
# FRONTEND_ORIGIN=https://scout.viagest.app,https://<frontend-domain>.up.railway.app
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
# Amadeus producción (vuelos reales) — developers.amadeus.com → My apps → Production
AMADEUS_API_KEY=<production_key>
AMADEUS_API_SECRET=<production_secret>
AMADEUS_BASE_URL=https://api.amadeus.com
# Opcional: Duffel LIVE (no duffel_test_*). Requiere cuenta comercial.
# DUFFEL_API_TOKEN=<live_token>
# DUFFEL_BASE_URL=https://api.duffel.com
# DUFFEL_VERSION=v2
```

### Demo pública (scout.viagest.app sin API live aún)

Si todavía no tenés Amadeus producción ni Duffel live, podés habilitar itinerarios **ficticios** de demostración (la UI ya avisa que no son reales):

```env
FLIGHT_PROVIDER=demo
FLIGHT_PROVIDERS=demo
ALLOW_DEMO_PROVIDER=true
ALLOW_DUFFEL_TEST=false
```

Cuando tengas credenciales live, volvé a `FLIGHT_PROVIDERS=amadeus` (o `duffel`) y desactivá `ALLOW_DEMO_PROVIDER`.

### Vuelos reales (importante)

- **`duffel_test_*` está deshabilitado** por defecto: no alimenta las estrategias en producción.
- **Recomendado para empezar:** [Amadeus Self-Service](https://developers.amadeus.com) con `AMADEUS_BASE_URL=https://api.amadeus.com`.
- Verificá `GET /health` en el backend: debe listar `active_providers: ["amadeus"]` y `uses_test_inventory: false`.
- El 401 de Duffel en telemetría suele ser token vacío, revocado o de test mientras `FLIGHT_PROVIDERS` sigue apuntando a `duffel`.

## 3. Frontend

Crear otro servicio apuntando a `frontend/`.

### Root Directory

`frontend`

### Build Command

```bash
npm run build
```

### Start Command

Si detecta `Procfile`, no hace falta tocar nada. Si queres dejarlo explicito:

```bash
npm run start -- --port $PORT
```

### Variables sugeridas

```env
NEXT_PUBLIC_API_BASE_URL=https://<backend-domain>.up.railway.app
```

## 4. Orden recomendado de deploy

1. deploy del backend
2. copiar el dominio publico del backend
3. setear `NEXT_PUBLIC_API_BASE_URL` en frontend
4. deploy del frontend
5. copiar el dominio del frontend
6. agregar **todos** los dominios del frontend a CORS del backend (`ALLOWED_ORIGINS` o `FRONTEND_ORIGIN`)
   - Con dominio custom: incluir `https://scout.viagest.app` además del `*.up.railway.app`
   - Si falta, el navegador bloquea `POST /api/v1/searches` con error CORS en la consola
7. redeploy backend si hace falta

## 5. Verificacion post-deploy

### Backend

- `GET /health`
- `POST /api/v1/searches`
- `GET /api/v1/searches/{id}`

### Frontend

- `/en`
- `/es`
- crear una busqueda
- abrir el mismo `search_id` en `en` y `es`

## 6. Notas practicas

- No uses `SQLite` en Railway para produccion.
- El backend ya tiene endpoint de `health`.
- El frontend ya soporta `es/en` y `X-Locale`.
- El primer arranque del backend crea tablas automaticamente.
