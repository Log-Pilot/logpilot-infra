# LogPilot local development

This repository contains the local integration setup for the first LogPilot iteration. The Compose stack starts PostgreSQL, Redis, the ingest API, and the processor. The query API and web explorer are planned for later phases.

## Prerequisites

- Docker Desktop or another Docker Engine with the Compose plugin.
- Python 3 for the seed script.
- Network access on the first build so Docker can download base images and Maven dependencies.

The app images use Java 21. You do not need a local Java installation to run the Compose stack.

## Get the required repositories

Keep these repositories as sibling folders because Compose uses relative build contexts:

```sh
git clone --branch codex/first-iteration-bootstrap https://github.com/Log-Pilot/logpilot-infra.git
git clone --branch codex/ingest-api-v1 https://github.com/Log-Pilot/logpilot-ingest-service.git
git clone --branch codex/processor-postgres-v1 https://github.com/Log-Pilot/logpilot-processor-service.git
```

## Start the local stack

From the `logpilot-infra` directory:

```sh
test -f .env || cp .env.example .env
docker compose up --build -d
docker compose ps
```

Compose waits for Redis and PostgreSQL health checks before starting the app containers. The ingest readiness check includes Redis; processor readiness includes Redis and PostgreSQL. The processor applies its Flyway migration on startup. To follow startup logs:

```sh
docker compose logs -f ingest-service processor-service
```

## Load repeatable demo events

After the services report healthy:

```sh
python3 scripts/seed-demo.py
```

The script submits five sample events, including checkout errors and a shared trace ID. Event IDs are stable between runs, so PostgreSQL stores only one row per demo event even if the script is run again. Timestamps use the current time so seeded data is recent. Ingest returns before asynchronous processing finishes; follow the processor logs if you want to observe processing.

The API is available at `http://localhost:8081`; PostgreSQL is at `127.0.0.1:5432` and Redis at `127.0.0.1:6379`. The processor's health endpoint is at `http://localhost:8082/actuator/health/readiness`. You can override host ports in `.env` with `INGEST_PORT`, `PROCESSOR_PORT`, `POSTGRES_PORT`, and `REDIS_PORT`. The seed script accepts `INGEST_URL` when the ingest API uses a different host/port, for example `INGEST_URL=http://127.0.0.1:18081 python3 scripts/seed-demo.py`.

The local database credentials in `.env.example` are for development only. Do not reuse them in a deployed environment or commit a real `.env` file.

## Stop, restart, or reset

Stop containers while preserving database and stream data:

```sh
docker compose down
```

Start them again:

```sh
docker compose up -d
```

Delete the local PostgreSQL and Redis volumes and start with empty state:

```sh
docker compose down -v
docker compose up --build -d
```

`down -v` permanently removes the local database and Redis stream data.

## Troubleshooting

- **A port is already in use:** change its host port in `.env`, then recreate the stack with `docker compose up -d`.
- **An app stays unhealthy:** inspect `docker compose logs <service>` and check that PostgreSQL and Redis became healthy first.
- **Image build fails downloading dependencies:** retry after network access to Docker registries and Maven Central is available.
- **Seed command cannot reach ingest:** check `docker compose ps`, wait until ingest is healthy, or set the correct `INGEST_URL`.
- **You want a clean demo state:** run `docker compose down -v`, then start the stack and seed again.

## What this local phase includes

The local stack demonstrates event ingestion, asynchronous Redis Stream processing, and PostgreSQL persistence. It does not yet include search endpoints, a web UI, authentication, Druid, cloud resources, or production secrets management. See the first-iteration and future-iterations plans in the workspace handoff documents for the remaining product steps.
