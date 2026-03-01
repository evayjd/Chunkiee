from fastapi import FastAPI
from app.api import query

app = FastAPI()

app.include_router(query.router)

@app.get("/")
def health():
    return {"status": "ok"}