# ADR 0001: First local end-to-end iteration

- **Status:** Accepted for the first iteration
- **Date:** 2026-10-28
- **Scope:** Local portfolio/demo implementation; no production deployment

## Context

The Log-Pilot organization has separate repositories for collector, ingestion, processing, querying, frontend, alerting, AI, and infrastructure. The checked-in service code is mostly Spring Boot starter applications; READMEs describe a larger proposed platform. The first iteration needs a narrow shared contract and a locally reproducible data path before adding source integrations, analytics clusters, AI, or cloud deployment.

## Decision

Build a local vertical slice with this flow:

```text
sample events / minimal file input
  → logpilot-ingest-service (HTTP validation)
  → Redis Streams (one local stream)
  → logpilot-processor-service (normalize and persist)
  → PostgreSQL (searchable log_events table)
  → logpilot-query-service (filtered read API)
  → logpilot-frontend (log explorer)
```

The `logpilot-infra` repository owns local orchestration and cross-repository development documentation. Individual service code remains in its existing repository. The frontend remains in `logpilot-frontend`.

### Contract and behavior

- The canonical event contract is `contracts/log-event.schema.json`; the batch request envelope is `contracts/ingest-request.schema.json`.
- Ingestion is `POST /api/v1/logs/ingest` and accepts an `events` array.
- Required event fields are `service`, `level`, `timestamp`, and `message`.
- `event_id` is an optional UUID. The ingest service generates it when missing. Producers should provide a stable ID when they need retries to be deduplicated.
- `org_id` is optional and defaults to `demo` for the local demonstration. This is not authentication, authorization, or tenant isolation.
- Levels are restricted to `TRACE`, `DEBUG`, `INFO`, `WARN`, and `ERROR`.
- Timestamps must be ISO-8601 date-time values including a timezone; persistence normalizes them to UTC.
- Batch validation is atomic: if any event is invalid, reject the whole request with a 4xx response and field/index errors. Do not enqueue a partial batch.
- A successful ingest response means events were accepted into Redis, not yet persisted to PostgreSQL.
- Redis publish failures must not return success.
- The initial queue is one stream, `logpilot:logs`, with one processor consumer group. Per-organization streams are deferred.
- PostgreSQL is the only log search store for this iteration. Do not add Druid.
- The processor acknowledges a message only after successful database commit. Malformed events should be isolated from healthy events through a documented dead-letter policy.
- Search supports service, level, and bounded time-range filters with bounded pagination and parameterized SQL.
- The first UI is a real client of the query API; it must not show hard-coded rows as live results.
- Authentication, production tenancy, cloud deployment, billing, notifications, anomaly detection, and LLM features are explicitly outside this iteration.

### Local developer setup

- Local infrastructure will be defined in `logpilot-infra` using Docker Compose for PostgreSQL and Redis, plus app containers only when the service Dockerfiles exist.
- The project must remain runnable without AWS credentials or external AI keys.
- A deterministic sample event generator/fixture is sufficient for the first demo; a production-grade collector is not required.
- Use the Angular family intended by the frontend README, but scaffold using a currently supported compatible version when implementation begins. Do not assume the README's Angular 17 version is current.
- No cloud resources are provisioned by this decision.

## Consequences

### Benefits

- All services share one stable event shape and one batch convention.
- The first demo exercises validation, asynchronous messaging, persistence, search, and UI.
- Local setup avoids Druid and cloud costs while retaining Redis Streams as a meaningful queue.
- Future collector and AI work can be added without blocking core search.

### Tradeoffs and limitations

- PostgreSQL is a pragmatic first store, not a commitment to keep all high-volume analytics there.
- A single Redis stream and local demo org do not provide production tenant isolation or high availability.
- Events submitted without a stable `event_id` cannot be reliably deduplicated across producer retries.
- Atomic batches are simpler to reason about, but one invalid event rejects otherwise valid events in the same request.
- Compose cannot be exercised on the current machine until Docker is installed.

## Implementation order

1. Add a contract test/fixture shared by the services.
2. Implement ingest DTO validation and Redis publishing.
3. Implement processor consumer and PostgreSQL migration/persistence.
4. Implement query filters and pagination.
5. Scaffold the frontend explorer.
6. Add local Compose, deterministic seed/demo flow, and end-to-end documentation.
7. Revisit delivery guarantees, auth, tenancy, and analytics only after the local slice works.

## Revisit this decision when

- Query measurements show PostgreSQL is insufficient for the target workload.
- Real users require multiple organizations, credential management, or access control.
- A production collector source is selected.
- There is evidence a separate service boundary is adding more coordination cost than value.

