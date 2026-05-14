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
FLIGHT_PROVIDER=duffel
FLIGHT_PROVIDERS=duffel
PROVIDER_TIMEOUTS=duffel:30,amadeus:25,demo:5
DEFAULT_CURRENCY=USD
ALLOWED_ORIGINS=https://<frontend-domain>.up.railway.app
DUFFEL_API_TOKEN=...
DUFFEL_BASE_URL=https://api.duffel.com
DUFFEL_VERSION=v2
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
AMADEUS_API_KEY=
AMADEUS_API_SECRET=
AMADEUS_BASE_URL=https://test.api.amadeus.com
```

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
6. agregarlo a `ALLOWED_ORIGINS` del backend
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
