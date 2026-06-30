from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.models.shelf import Shelf
from app.crud.crud_sharing import shelf_share as crud_shelf_share

def check_shelf_permission(db: Session, shelf_id: int, current_user: User, required_role: str) -> Shelf:
    
    shelf = db.query(Shelf).filter(Shelf.id == shelf_id).first()
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")

    if shelf.owner_id == current_user.id:
        return shelf

    share = crud_shelf_share.get_by_shelf_and_user(db=db, shelf_id=shelf_id, user_id=current_user.id)
    if not share:
        raise HTTPException(status_code=403, detail="Not authorized to access this shelf")

    role_values = {"viewer": 1, "editor": 2, "owner": 3}
    user_role_val = role_values.get(share.role.value, 0)
    required_val = role_values.get(required_role, 3)

    if user_role_val < required_val:
        raise HTTPException(status_code=403, detail=f"Requires {required_role} access")

    return shelf
