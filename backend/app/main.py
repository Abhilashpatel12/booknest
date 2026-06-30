from fastapi import FastAPI
from app.api import (
    auth_router,
    book_router,
    shelf_router,
    sharing_router,
    lending_router,
    dashboard_router,
    websockets_router
)
from app.models import User, Book, Shelf, ShelfShare, Lending, Activity
from app.core.database import engine, Base
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title = "BookNest API",
    version = "1.0.0"
)

app.include_router(auth_router)
app.include_router(book_router)
app.include_router(shelf_router)
app.include_router(sharing_router)
app.include_router(lending_router)
app.include_router(dashboard_router)
app.include_router(websockets_router)

@app.get("/")
def root():
    return {"message":"welcome to booknest api"}
