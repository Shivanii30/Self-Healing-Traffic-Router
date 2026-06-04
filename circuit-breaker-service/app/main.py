from fastapi import FastAPI, HTTPException, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.registry import breakers

app = FastAPI()


@app.get("/allow/{service_name}")
async def allow(service_name: str):
    breaker = breakers.get(service_name)
    if not breaker:
        raise HTTPException(status_code=404, detail="service not found")

    if breaker.allow_request():
        return {"allowed": True, "state": breaker.state}

    raise HTTPException(
        status_code=503,
        detail={"error": "service unavailable", "state": breaker.state},
    )


@app.post("/success/{service_name}")
async def success(service_name: str):
    breaker = breakers.get(service_name)
    if not breaker:
        raise HTTPException(status_code=404, detail="service not found")
    breaker.record_success()
    breaker.save_to_redis(service_name)
    return breaker.status()


@app.post("/failure/{service_name}")
async def failure(service_name: str):
    breaker = breakers.get(service_name)
    if not breaker:
        raise HTTPException(status_code=404, detail="service not found")
    breaker.record_failure()
    breaker.save_to_redis(service_name)
    return breaker.status()


@app.get("/status/{service_name}")
async def status(service_name: str):
    breaker = breakers.get(service_name)
    if not breaker:
        raise HTTPException(status_code=404, detail="service not found")
    return breaker.status()


@app.post("/recover/{service_name}")
async def recover(service_name: str):
    breaker = breakers.get(service_name)
    if not breaker:
        raise HTTPException(status_code=404, detail="service not found")
    breaker.recover()
    breaker.save_to_redis(service_name)
    return breaker.status()


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
