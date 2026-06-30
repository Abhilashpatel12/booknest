from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.sharing import ShelfShare
from pydantic import BaseModel

# Internal schemas for CRUD
class ShelfShareCreate(BaseModel):
    shelf_id: int
    user_id: int
    role: str

class ShelfShareUpdate(BaseModel):
    role: str

class CRUDShelfShare(CRUDBase[ShelfShare, ShelfShareCreate, ShelfShareUpdate]):
    def get_by_shelf_and_user(self, db: Session, shelf_id: int, user_id: int) -> ShelfShare:
        return db.query(self.model).filter(
            self.model.shelf_id == shelf_id,
            self.model.user_id == user_id
        ).first()

    def create(self, db: Session, *, obj_in: ShelfShareCreate) -> ShelfShare:
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

shelf_share = CRUDShelfShare(ShelfShare)
