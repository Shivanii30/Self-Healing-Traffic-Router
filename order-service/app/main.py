from fastapi import FastAPI

app = FastAPI()

@app.get("/orders")
async def orders():
    return {"service": "order", "data": []}

@app.get("/health")
async def health():
    return {"status": "healthy"}
