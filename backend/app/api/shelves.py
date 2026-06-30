from app.core.dependencies import get_current_user, get_db
from app.core.activity import log_activity
from app.core.permissions import check_shelf_permission
from datetime import datetime, timezone
import asyncio
from typing import List, Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models import User, Book, Shelf, BookStatus, Lending, Activity, ShelfShare, ShareRole
from app.schemas import BookCreate, BookResponse, BookUpdate, ShelfCreate, ShelfResponse, ShelfUpdate, LendBookRequest, LendingResponse, ShareShelfRequest, UpdateRoleRequest, SharedUserResponse, SignupRequest, LoginRequest, RefreshTokenRequest
from sqlalchemy.orm import Session
from app.models import shelf as shelf_models
from app.models import book as book_models
from app.crud import shelf as crud_shelf
from app.api.books import get_book_by_id
from app.api.websockets import manager

router = APIRouter(prefix="/shelves",tags=["shelves"])

@router.get("/", response_model=List[ShelfResponse])
def get_shelves(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud_shelf.get_multi(db=db, owner_id=current_user.id)

@router.post("/",response_model=ShelfResponse)
def create_shelf(shelf: ShelfCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_shelf = crud_shelf.create(db=db, obj_in=shelf, owner_id=current_user.id)
    log_activity(db, current_user.id, "SHELF_CREATED", f"Created a new shelf: '{new_shelf.name}'")
    return new_shelf

@router.get("/{shelf_id}",response_model=ShelfResponse)
def get_shelf_by_id(shelf_id: int,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    
    db_shelf = check_shelf_permission(db=db, shelf_id=shelf_id, current_user=current_user, required_role="viewer")
    return db_shelf 

@router.put("/{shelf_id}", response_model=ShelfResponse)
def update_shelf(shelf_id: int, shelf_update: ShelfUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    db_shelf = check_shelf_permission(db=db, shelf_id=shelf_id, current_user=current_user, required_role="editor")
    

    return crud_shelf.update(db=db, db_obj=db_shelf, obj_in=shelf_update)

@router.delete("/{shelf_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_shelf(shelf_id:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    # Only owners can delete the shelf itself
    db_shelf = check_shelf_permission(db=db, shelf_id=shelf_id, current_user=current_user, required_role="owner")
    db.delete(db_shelf)
    db.commit()
    return None

@router.post("/{shelf_id}/books/{book_id}",response_model=ShelfResponse)
def add_book_to_shelf(shelf_id:int,book_id:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    
    db_shelf = check_shelf_permission(db=db, shelf_id=shelf_id, current_user=current_user, required_role="editor")
    
   
    db_book = get_book_by_id(book_id=book_id, db=db, current_user=current_user)
    
    if db_book in db_shelf.books:
        raise HTTPException(status_code=400, detail = "book already exists on this shelf")
        
    db_shelf.books.append(db_book)
    db.commit()
    db.refresh(db_shelf)
    
    ws_msg = {"type": "SHELF_UPDATED", "shelf_id": shelf_id}
    recipients = [db_shelf.owner_id] + [share.user_id for share in db_shelf.shares]
    for uid in set(recipients):
        if uid != current_user.id:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(manager.send_personal_message(ws_msg, uid))
            except RuntimeError:
                asyncio.run(manager.send_personal_message(ws_msg, uid))
                
    return db_shelf

@router.delete("/{shelf_id}/books/{book_id}",status_code=status.HTTP_204_NO_CONTENT)
def remove_book_from_shelf(shelf_id:int,book_id:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
   
    db_shelf = check_shelf_permission(db=db, shelf_id=shelf_id, current_user=current_user, required_role="editor")
    
   
    db_book = db.query(book_models.Book).filter(book_models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="book not found")
    
    if db_book not in db_shelf.books:
        raise HTTPException(status_code=400, detail="book doesnt exist on this shelf")
        
    db_shelf.books.remove(db_book)
    db.commit()
    
    ws_msg = {"type": "SHELF_UPDATED", "shelf_id": shelf_id}
    recipients = [db_shelf.owner_id] + [share.user_id for share in db_shelf.shares]
    for uid in set(recipients):
        if uid != current_user.id:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(manager.send_personal_message(ws_msg, uid))
            except RuntimeError:
                asyncio.run(manager.send_personal_message(ws_msg, uid))
                
    return None