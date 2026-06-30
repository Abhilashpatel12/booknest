from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum
from app.models.associations import book_shelf_association
from sqlalchemy.orm import relationship

class BookStatus(str,enum.Enum):
    WANT_TO_READ = "want to read"
    READING = "reading"
    FINISHED = "finished"


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer,primary_key = True,index = True)
    owner_id = Column(Integer,ForeignKey("users.id"))
    title = Column(String(255),nullable = False)
    author = Column(String(255),nullable=False)
    status = Column(Enum(BookStatus),default=BookStatus.WANT_TO_READ)
    total_pages = Column(Integer,nullable=False)
    current_page = Column(Integer,default = 0)
    rating = Column(Integer,nullable = True)
    notes = Column(String,nullable =True)
    finished_date = Column(DateTime(timezone=True),nullable = True)
    created_at = Column(DateTime(timezone=True),server_default =func.now())
    updated_at = Column(DateTime(timezone=True),onupdate=func.now())
    shelves = relationship("Shelf", secondary=book_shelf_association, back_populates="books")