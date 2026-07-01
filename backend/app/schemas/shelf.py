from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.book import BookResponse

class ShelfBase(BaseModel):
    name: str

class ShelfCreate(ShelfBase):
    pass

class ShelfUpdate(BaseModel):
    name: Optional[str] = None

from app.schemas.sharing import SharedUserResponse

class ShelfResponse(ShelfBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    books: List[BookResponse] = []
    shares: List[SharedUserResponse] = []

    model_config = ConfigDict(from_attributes=True)