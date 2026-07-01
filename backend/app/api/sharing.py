from app.core.dependencies import get_current_user, get_db
from app.core.activity import log_activity
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.models import User, Book, Shelf, BookStatus, Lending, Activity, ShelfShare, ShareRole
from app.schemas import BookCreate, BookResponse, BookUpdate, ShelfCreate, ShelfResponse, ShelfUpdate, LendBookRequest, LendingResponse, ShareShelfRequest, UpdateRoleRequest, SharedUserResponse, SignupRequest, LoginRequest, RefreshTokenRequest
from sqlalchemy.orm import Session
from app.crud import shelf as crud_shelf
from app.crud import shelf_share as crud_shelf_share
from app.crud.crud_sharing import ShelfShareCreate, ShelfShareUpdate

router = APIRouter(prefix="/sharing", tags=["sharing"])

@router.post("/shelves/{shelf_id}", status_code=status.HTTP_201_CREATED)
def share_shelf(shelf_id: int, request: ShareShelfRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    db_shelf = crud_shelf.get(db=db, id=shelf_id, owner_id=current_user.id)
    if not db_shelf:
        
        exists = db.query(crud_shelf.model).filter(crud_shelf.model.id == shelf_id).first()
        if exists:
            raise HTTPException(status_code=403, detail="Not authorized to share this shelf")
        raise HTTPException(status_code=404, detail="Shelf not found")

    
    target_user = db.query(User).filter(User.email == request.email.lower()).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot share shelf with yourself")

    existing_share = crud_shelf_share.get_by_shelf_and_user(db=db, shelf_id=shelf_id, user_id=target_user.id)
    if existing_share:
        raise HTTPException(status_code=409, detail="Shelf already shared with this user")

    share_in = ShelfShareCreate(shelf_id=shelf_id, user_id=target_user.id, role=request.role)
    new_share = crud_shelf_share.create(db=db, obj_in=share_in)
    
    log_activity(db, current_user.id, "SHELF_SHARED", f"Shared shelf '{db_shelf.name}' with {target_user.name} as {request.role}")
    
    return {"message": "Shelf shared successfully"}

@router.get("/shared-with-me", response_model=List[ShelfResponse])
def get_shared_shelves(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
 
    shares = db.query(ShelfShare).filter(ShelfShare.user_id == current_user.id).all()
    shelves = [share.shelf for share in shares]
    return shelves

@router.put("/{share_id}")
def update_role(share_id: int, request: UpdateRoleRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    share = db.query(ShelfShare).filter(ShelfShare.id == share_id).first()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
        
    shelf = crud_shelf.get(db=db, id=share.shelf_id, owner_id=current_user.id)
    if not shelf:
        raise HTTPException(status_code=403, detail="Not authorized to update roles on this shelf")
        
    share.role = request.role
    db.commit()
    db.refresh(share)
    
    target_user = db.query(User).filter(User.id == share.user_id).first()
    log_activity(db, current_user.id, "COLLABORATOR_ROLE_CHANGED", f"Updated {target_user.name}'s role to {request.role} on shelf '{shelf.name}'")
    
    return {"message": "Role updated successfully"}

@router.delete("/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_collaborator(share_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
   
    share = db.query(ShelfShare).filter(ShelfShare.id == share_id).first()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
        
    shelf = crud_shelf.get(db=db, id=share.shelf_id, owner_id=current_user.id)
    if not shelf:
        raise HTTPException(status_code=403, detail="Not authorized to remove collaborators from this shelf")
        
    target_user = db.query(User).filter(User.id == share.user_id).first()
    db.delete(share)
    db.commit()
    
    log_activity(db, current_user.id, "COLLABORATOR_REMOVED", f"Removed {target_user.name} from shelf '{shelf.name}'")
    
    return None
