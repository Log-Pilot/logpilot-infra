#!/usr/bin/env python3
"""Post a small, repeatable set of demo events to the local ingest API."""

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone


BASE_URL = os.environ.get("INGEST_URL", "http://127.0.0.1:8081")
HEALTH_URL = f"{BASE_URL.rstrip('/')}/actuator/health/readiness"
INGEST_URL = f"{BASE_URL.rstrip('/')}/api/v1/logs/ingest"
EVENTS = [
    {
        "event_id": "d0c2ca10-f778-4f4d-89a2-005b3fc49c10",
        "org_id": "demo",
        "service": "checkout-api",
        "level": "INFO",
        "timestamp": "2026-01-15T10:00:00Z",
        "message": "Checkout request received",
        "trace_id": "trace-checkout-demo-001",
        "metadata": {"environment": "local", "host": "demo-machine"},
    },
    {
        "event_id": "9f31e201-18ea-4c0f-b9e9-c7f0ef2a5c92",
        "org_id": "demo",
        "service": "checkout-api",
        "level": "WARN",
        "timestamp": "2026-01-15T10:00:01Z",
        "message": "Payment provider response exceeded 500 ms",
        "trace_id": "trace-checkout-demo-001",
        "metadata": {"environment": "local", "duration_ms": 642},
    },
    {
        "event_id": "6c304ed0-1c14-44c6-82c1-5940f10be194",
        "org_id": "demo",
        "service": "checkout-api",
        "level": "ERROR",
        "timestamp": "2026-01-15T10:00:02Z",
        "message": "Payment authorization failed: provider timeout",
        "trace_id": "trace-checkout-demo-001",
        "metadata": {"environment": "local", "error_code": "PAYMENT_TIMEOUT"},
    },
    {
        "event_id": "9b394be5-6bdf-4661-9da2-5eb538b4be8e",
        "org_id": "demo",
        "service": "inventory-api",
        "level": "INFO",
        "timestamp": "2026-01-15T10:00:03Z",
        "message": "Inventory reservation created",
        "trace_id": "trace-checkout-demo-001",
        "metadata": {"environment": "local", "sku": "SKU-1001"},
    },
    {
        "event_id": "bc54047a-4a42-4554-a38c-6f3cdcd7b9a0",
        "org_id": "demo",
        "service": "identity-api",
        "level": "ERROR",
        "timestamp": "2026-01-15T10:04:00Z",
        "message": "Token validation rejected an expired token",
        "trace_id": "trace-identity-demo-002",
        "metadata": {"environment": "local", "error_code": "TOKEN_EXPIRED"},
    },
]


def wait_until_ready(timeout_seconds=60):
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2)
    raise SystemExit(f"Ingest API did not become ready at {HEALTH_URL}")


def main():
    wait_until_ready()
    start_time = datetime.now(timezone.utc).replace(microsecond=0)
    for index, event in enumerate(EVENTS):
        event["timestamp"] = (start_time + timedelta(seconds=index)).isoformat().replace("+00:00", "Z")
    request = urllib.request.Request(
        INGEST_URL,
        data=json.dumps({"events": EVENTS}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8")
            print(f"Ingest API returned HTTP {response.status}: {body}")
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Ingest failed with HTTP {error.code}: {detail}") from error

    print(f"Submitted {len(EVENTS)} deterministic demo events.")
    print("Re-running is safe: the processor deduplicates stored rows by event_id.")


if __name__ == "__main__":
    main()
