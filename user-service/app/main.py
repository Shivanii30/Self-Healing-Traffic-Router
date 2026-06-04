from fastapi import FastAPI

app = FastAPI()

@app.get("/users")
async def users():
    return {"service": "user", "data": []}

@app.get("/health")
async def health():
    return {"status": "healthy"}
