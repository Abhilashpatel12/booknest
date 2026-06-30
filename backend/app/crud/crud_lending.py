from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.lending import Lending
from pydantic import BaseModel

class LendingCreate(BaseModel):
    book_id: int
    lender_id: int
    borrower_id: int

class LendingUpdate(BaseModel):
    is_active: bool
    returned_at: str


class CRUDLending(CRUDBase[Lending, LendingCreate, LendingUpdate]):
    
    def get_active_lend(self, db: Session, book_id: int) -> Optional[Lending]:
        
        return db.query(self.model).filter(
            self.model.book_id == book_id,
            self.model.is_active == True
        ).first()

lending = CRUDLending(Lending)
