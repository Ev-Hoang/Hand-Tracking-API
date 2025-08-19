from fastapi import FastAPI
from app.api import routes

app = FastAPI(title="FastAPI + AI + STM32")

# include API routes
app.include_router(routes.router)

@app.get("/")
def root():
    return {"msg": "FastAPI server running!"}