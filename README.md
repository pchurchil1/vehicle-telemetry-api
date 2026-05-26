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
- Vehicle create, get, and paginated list endpoints
- ECU create, get, and paginated vehicle-scoped list endpoints
- Event ingestion, detail lookup, vehicle-scoped querying, and filtering by ECU, event type, and created-at range
- Vehicle telemetry summary with ECU count, event count, latest event timestamp, and event counts by type
- SQLAlchemy models, repository/service layering, and Alembic migrations for telemetry tables, constraints, and indexes

## Local Development

Copy `.env.example` to `.env`, then start the API and database:

```bash
docker compose up --build
```

Run migrations inside the API container:

```bash
docker compose exec api alembic upgrade head
```

Run tests:

```bash
docker compose exec api pytest -q
```
