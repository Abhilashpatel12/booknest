from app.core.dependencies import get_current_user, get_db
from app.core.activity import log_activity
from datetime import datetime, timezone
from typing import List, Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models import User, Book, Shelf, BookStatus, Lending, Activity, ShelfShare, ShareRole
from app.schemas import BookCreate, BookResponse, BookUpdate, ShelfCreate, ShelfResponse, ShelfUpdate, LendBookRequest, LendingResponse, ShareShelfRequest, UpdateRoleRequest, SharedUserResponse, SignupRequest, LoginRequest, RefreshTokenRequest
from sqlalchemy.orm import Session
from app.crud import book as crud_book

router = APIRouter(
    prefix="/books",
    tags =["books"]
)

@router.post("/",response_model=BookResponse)
def create_book(book: BookCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_book = crud_book.create(db=db, obj_in=book, owner_id=current_user.id)
    
    log_activity(db, current_user.id, "BOOK_ADDED", f"Added '{new_book.title}' to library.")
    
    return new_book

@router.get("/",response_model=List[BookResponse]) 
def get_books(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
    status: Optional[BookStatus] = None,
    search: Optional[str] = None,
    sort_by: Literal["rating", "title", "date_added"] = "date_added",
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    skip = (page - 1) * limit
    return crud_book.get_multi_filtered(
        db=db,
        owner_id=current_user.id,
        skip=skip,
        limit=limit,
        book_status=status,
        search=search,
        sort_by=sort_by
    )

@router.get("/{book_id}",response_model=BookResponse)
def get_book_by_id(book_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    book = crud_book.get(db=db, id=book_id, owner_id=current_user.id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="book not found"
        )
    return book

@router.put("/{book_id}",response_model=BookResponse)
def update_book(book_id: int, book_update: BookUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_book = crud_book.get(db=db, id=book_id, owner_id=current_user.id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="book not found")
        
    try:
        return crud_book.update(db=db, db_obj=db_book, obj_in=book_update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{book_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_book = crud_book.get(db=db, id=book_id, owner_id=current_user.id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="book not found")
    crud_book.remove(db=db, id=book_id, owner_id=current_user.id)
    return None
