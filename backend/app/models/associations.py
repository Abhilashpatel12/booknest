from sqlalchemy import Table, Column, Integer, ForeignKey
from app.core.database import Base


book_shelf_association = Table(
    "book_shelf_association",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("shelf_id", Integer, ForeignKey("shelf.id"), primary_key=True)
)