import asyncio
import json
import time
import httpx

from app.registry import SERVICES, CIRCUIT_BREAKER_URL
from app.redis_client import redis_client
from app.metrics import SERVICE_CHECKS_TOTAL, UNHEALTHY_SERVICES_TOTAL

failure_counts: dict = {}
last_status: dict = {}


async def check_service(service_name: str, service_url: str):
    SERVICE_CHECKS_TOTAL.inc()
    start = time.perf_counter()

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{service_url}/health")

        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        if response.status_code == 200:
            previous_status = last_status.get(service_name, "unknown")
            last_status[service_name] = "healthy"

            # Self-healing: service recovered — notify circuit-breaker
            if previous_status == "unhealthy":
                try:
                    async with httpx.AsyncClient(timeout=2.0) as client:
                        await client.post(
                            f"{CIRCUIT_BREAKER_URL}/recover/{service_name}"
                        )
                except Exception:
                    pass

            failure_counts.setdefault(service_name, 0)
            data = {
                "status": "healthy",
                "latency_ms": latency_ms,
                "failures": failure_counts[service_name],
            }

        else:
            UNHEALTHY_SERVICES_TOTAL.inc()
            failure_counts.setdefault(service_name, 0)
            failure_counts[service_name] += 1
            last_status[service_name] = "unhealthy"

            # Notify circuit-breaker of failure
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    await client.post(
                        f"{CIRCUIT_BREAKER_URL}/failure/{service_name}"
                    )
            except Exception:
                pass

            data = {
                "status": "unhealthy",
                "latency_ms": latency_ms,
                "failures": failure_counts[service_name],
            }

    except Exception:
        UNHEALTHY_SERVICES_TOTAL.inc()
        last_status[service_name] = "unhealthy"
        failure_counts.setdefault(service_name, 0)
        failure_counts[service_name] += 1

        # Notify circuit-breaker of connection failure
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                await client.post(
                    f"{CIRCUIT_BREAKER_URL}/failure/{service_name}"
                )
        except Exception:
            pass

        data = {
            "status": "unhealthy",
            "latency_ms": -1,
            "failures": failure_counts[service_name],
        }

    # Write to Redis with consistent key "service_status:<name>"
    redis_client.set(f"service_status:{service_name}", json.dumps(data))
    return data


async def monitor_loop():
    while True:
        tasks = [
            check_service(name, url) for name, url in SERVICES.items()
        ]
        await asyncio.gather(*tasks)
        await asyncio.sleep(0.5)
