import time
from fastapi import FastAPI, HTTPException, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.router import get_destination
from app.metrics import REQUESTS_TOTAL, ERRORS_TOTAL, REQUEST_DURATION

app = FastAPI()


@app.get("/")
async def root():
    return {"service": "routing-engine"}


@app.get("/resolve/{service_name}")
async def resolve(service_name: str):
    REQUESTS_TOTAL.inc()
    start = time.perf_counter()

    destination = get_destination(service_name)

    REQUEST_DURATION.observe(time.perf_counter() - start)

    if not destination:
        ERRORS_TOTAL.inc()
        raise HTTPException(status_code=503, detail="No healthy instances available")

    return {"service": service_name, "destination": destination}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
