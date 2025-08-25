from fastapi import FastAPI
from app.api import router   # router nằm trong __init__.py

app = FastAPI()
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Hello FastAPI!"}