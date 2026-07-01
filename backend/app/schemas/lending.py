from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class LendBookRequest(BaseModel):
    borrower_email: EmailStr

    def get_email(self):
        return self.borrower_email.lower().strip()


class LendingUser(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class LendingBook(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)

class LendingResponse(BaseModel):
    id: int
    book_id: int
    lender_id: int
    borrower_id: int
    borrowed_at: datetime
    returned_at: Optional[datetime]
    is_active: bool
    
    book: LendingBook
    lender: LendingUser
    borrower: LendingUser

    model_config = ConfigDict(from_attributes=True)
