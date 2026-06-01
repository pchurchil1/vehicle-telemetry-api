.PHONY: up down build migrate test test-postgres logs shell

up:
	docker compose up --build

down:
	docker compose down

build:
	docker compose build

migrate:
	docker compose exec api alembic upgrade head

test:
	docker compose exec api pytest -q

test-postgres:
	docker compose exec db psql -U app -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'telemetry_test'" | grep -q 1 || docker compose exec db createdb -U app telemetry_test
	docker compose exec -e ENVIRONMENT=test -e RUN_POSTGRES_TESTS=1 api pytest -q -m postgres

logs:
	docker compose logs -f api

shell:
	docker compose exec api /bin/sh
