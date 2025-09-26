from fastapi import FastAPI

from .routers import api_router

app = FastAPI(title="TL-Forge API", version="2.0")
app.include_router(api_router)


@app.get("/")
def read_root() -> dict:
    return {"message": "Welcome to TL-Forge API"}
