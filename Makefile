.PHONY: up down build migrate test logs shell

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

logs:
	docker compose logs -f api

shell:
	docker compose exec api /bin/sh
