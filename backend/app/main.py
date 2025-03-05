from fastapi import FastAPI
from app.api import general_adapter, auth

app = FastAPI()

app.include_router(general_adapter.router, prefix="/api", tags=["API Adapter"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])


@app.get("/")
async def root():
    return {"message": "Check4Parts API adapter is running"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
