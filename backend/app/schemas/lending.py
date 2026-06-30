from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class LendBookRequest(BaseModel):
    borrower_email: EmailStr


class LendingResponse(BaseModel):
    id: int
    book_id: int
    lender_id: int
    borrower_id: int
    borrowed_at: datetime
    returned_at: Optional[datetime]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
