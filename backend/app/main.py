from fastapi import FastAPI
from app.api.auth import router as auth_router

app = FastAPI(
    title = "BookNest API",
    version = "1.0.0"
)

app.include_router(auth_router)

@app.get("/")
def root():
    return {"message":"welcome to booknest api"}
