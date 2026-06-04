from fastapi import FastAPI

app = FastAPI()

@app.get("/payments")
async def payments():
    return {"service": "payment", "data": []}

@app.get("/health")
async def health():
    return {"status": "healthy"}
