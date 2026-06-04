import os
import time
import httpx
from fastapi import FastAPI, HTTPException, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.metrics import REQUESTS_TOTAL, ERRORS_TOTAL, REQUEST_DURATION

app = FastAPI()

ROUTING_ENGINE = os.environ.get("ROUTING_ENGINE_URL", "http://routing-engine-service:9000")


async def route_request(service_name: str, path: str):
    """Resolve a healthy instance via the routing engine, then forward."""
    REQUESTS_TOTAL.labels(route=service_name).inc()
    start = time.perf_counter()

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resolve_resp = await client.get(
                f"{ROUTING_ENGINE}/resolve/{service_name}"
            )
        if resolve_resp.status_code != 200:
            raise HTTPException(status_code=503, detail="No healthy instances")

        destination = resolve_resp.json()["destination"]

        # Map logical name → actual Docker service URL
        service_map = {
            "user-v1": "http://user-service:8001",
            "payment-v1": "http://payment-service:8002",
            "order-v1": "http://order-service:8003",
        }
        base_url = service_map.get(destination)
        if not base_url:
            raise HTTPException(status_code=503, detail="Unknown destination")

        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base_url}{path}")

        REQUEST_DURATION.labels(route=service_name).observe(time.perf_counter() - start)
        return resp.json()

    except HTTPException:
        ERRORS_TOTAL.labels(route=service_name).inc()
        raise
    except Exception as e:
        ERRORS_TOTAL.labels(route=service_name).inc()
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/api/users")
async def get_users():
    return await route_request("user-service", "/users")


@app.get("/api/payments")
async def get_payments():
    return await route_request("payment-service", "/payments")


@app.get("/api/orders")
async def get_orders():
    return await route_request("order-service", "/orders")


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
async def health():
    return {"status": "healthy"}
