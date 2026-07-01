from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.book import BookStatus

class BookBase(BaseModel):
    title: str
    author: str
    total_pages: int
    status: BookStatus = BookStatus.WANT_TO_READ
    current_page: int = 0
    rating: Optional[int] = Field(default=None, ge=0, le=5)
    notes: Optional[str] = None
    finished_date: Optional[datetime] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    total_pages: Optional[int] = None
    status: Optional[BookStatus] = None
    current_page: Optional[int] = None
    rating: Optional[int] = Field(default=None, ge=0, le=5)
    notes: Optional[str] = None
    finished_date: Optional[datetime] = None

class BookResponse(BookBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class PaginatedBookResponse(BaseModel):
    items: List[BookResponse]
    total: int
    page: int
    pages: int
