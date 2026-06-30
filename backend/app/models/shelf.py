from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.core.database import Base
from sqlalchemy.orm import relationship
from app.models.associations import book_shelf_association



class Shelf(Base):
    __tablename__ = "shelf"
    
    id = Column(Integer,primary_key = True,index = True)
    owner_id = Column(Integer,ForeignKey("users.id"))
    name = Column(String(255), nullable= False)
    created_at = Column(DateTime(timezone=True),server_default =func.now())
    updated_at = Column(DateTime(timezone=True),onupdate=func.now())
    books = relationship("Book", secondary=book_shelf_association, back_populates="shelves")
    shares = relationship("ShelfShare", backref="shelf", cascade="all, delete-orphan")