# vehicle-telemetry-api

Production-grade FastAPI backend for vehicle telemetry ingestion, querying, and event processing.

## Goal

Design and implement a production-grade telemetry backend similar to what might exist inside an OEM or Tier-1 supplier.

## Stack

FastAPI · PostgreSQL · Docker · Alembic · Pytest

## Status

Phase 1 — core telemetry API

Implemented:

- Health and database health checks
- Vehicle create, get, update, delete, filtered search, and paginated list endpoints
- ECU create, get, update, delete, and paginated vehicle-scoped list endpoints
- Event ingestion, batch ingestion, detail lookup, vehicle-scoped querying, and filtering by ECU, event type, and created-at range
- Structured JSON telemetry payloads backed by PostgreSQL JSONB
- Vehicle telemetry summary with ECU count, event count, latest event timestamp, and event counts by type
- Consistent JSON error responses
- Optional API key authentication with `X-API-Key`
- SQLAlchemy models, repository/service layering, and Alembic migrations for telemetry tables, constraints, and indexes

## Local Development

Copy `.env.example` to `.env`, then start the API and database:

```bash
docker compose up --build
```

Or use:

```bash
make up
```

Run migrations inside the API container:

```bash
docker compose exec api alembic upgrade head
```

Or:

```bash
make migrate
```

Run tests:

```bash
docker compose exec api pytest -q
```

Or:

```bash
make test
```

## API Examples

Create a vehicle:

```bash
curl -X POST http://localhost:8000/api/v1/vehicles \
  -H "Content-Type: application/json" \
  -d '{"vin":"1FTFW1RG0PFA12345","make":"Ford","model":"F-150","year":2024}'
```

Create an event with a structured telemetry payload:

```bash
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{"vehicle_id":1,"ecu_id":null,"event_type":"DTC","payload":{"code":"P0300","severity":"warning","odometer_miles":42108}}'
```

Batch ingest events:

```bash
curl -X POST http://localhost:8000/api/v1/events/batch \
  -H "Content-Type: application/json" \
  -d '{"events":[{"vehicle_id":1,"ecu_id":null,"event_type":"INFO","payload":{"message":"boot"}},{"vehicle_id":1,"ecu_id":null,"event_type":"DTC","payload":{"code":"U0100"}}]}'
```

Filter vehicles:

```bash
curl "http://localhost:8000/api/v1/vehicles?make=Ford&model=F-150&year=2024&vin_prefix=1FT"
```

View telemetry summary:

```bash
curl http://localhost:8000/api/v1/vehicles/1/telemetry/summary
```

## Optional API Key

Set `API_KEY` in `.env` to require `X-API-Key` on vehicle, ECU, and event endpoints:

```bash
API_KEY=dev-secret
```

Then call endpoints with:

```bash
curl http://localhost:8000/api/v1/vehicles \
  -H "X-API-Key: dev-secret"
```
