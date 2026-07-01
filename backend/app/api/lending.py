from app.core.dependencies import get_current_user, get_db
from app.core.activity import log_activity
from typing import List
from datetime import datetime, timezone
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from app.models import User, Book, Shelf, BookStatus, Lending, Activity, ShelfShare, ShareRole
from app.schemas import BookCreate, BookResponse, BookUpdate, ShelfCreate, ShelfResponse, ShelfUpdate, LendBookRequest, LendingResponse, ShareShelfRequest, UpdateRoleRequest, SharedUserResponse, SignupRequest, LoginRequest, RefreshTokenRequest
from sqlalchemy.orm import Session
from app.crud import book as crud_book
from app.crud import lending as crud_lending
from app.crud.crud_lending import LendingCreate
from app.api.websockets import manager

router = APIRouter(prefix="/lending", tags=["lending"])

@router.post("/{book_id}/lend", response_model=LendingResponse)
def lend_book(book_id: int, request: LendBookRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    db_book = crud_book.get(db=db, id=book_id, owner_id=current_user.id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

   
    borrower = db.query(User).filter(User.email == request.get_email()).first()
    if not borrower:
        raise HTTPException(status_code=404, detail="User not found")

    if borrower.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot lend a book to yourself")

   
    active_lend = crud_lending.get_active_lend(db=db, book_id=book_id)
    if active_lend:
        raise HTTPException(status_code=409, detail="Book is already lent out")

    
    lending_in = LendingCreate(book_id=book_id, lender_id=current_user.id, borrower_id=borrower.id)

    new_lend = Lending(
        book_id=book_id,
        lender_id=current_user.id,
        borrower_id=borrower.id
    )
    db.add(new_lend)
    db.commit()
    db.refresh(new_lend)
    

    log_activity(db, current_user.id, "BOOK_LENT", f"Lent '{db_book.title}' to {borrower.name}")
    
    ws_msg = {"type": "BOOK_LENT_TO_YOU", "book_id": book_id, "lender_id": current_user.id}
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(manager.send_personal_message(ws_msg, borrower.id))
    except RuntimeError:
        asyncio.run(manager.send_personal_message(ws_msg, borrower.id))
    
    return new_lend

@router.post("/{lend_id}/return", response_model=LendingResponse)
def return_book(lend_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
  
    lend_record = db.query(Lending).filter(Lending.id == lend_id).first()
    if not lend_record:
        raise HTTPException(status_code=404, detail="Lending record not found")

    
    if current_user.id not in [lend_record.lender_id, lend_record.borrower_id]:
        raise HTTPException(status_code=403, detail="Not authorized to return this book")

   
    if not lend_record.is_active:
        raise HTTPException(status_code=400, detail="Book is already returned")

    
    lend_record.is_active = False
    lend_record.returned_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(lend_record)

    db_book = crud_book.get(db=db, id=lend_record.book_id, owner_id=lend_record.lender_id)
    book_title = db_book.title if db_book else "a book"
    
    log_activity(db, current_user.id, "BOOK_RETURNED", f"Returned '{book_title}'")
    
    other_party_id = lend_record.borrower_id if current_user.id == lend_record.lender_id else lend_record.lender_id
    ws_msg = {"type": "BOOK_RETURNED", "book_id": lend_record.book_id, "lend_id": lend_record.id}
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(manager.send_personal_message(ws_msg, other_party_id))
    except RuntimeError:
        asyncio.run(manager.send_personal_message(ws_msg, other_party_id))

    return lend_record

@router.get("/borrowed", response_model=List[LendingResponse])
def get_borrowed_books(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    records = db.query(Lending).filter(
        Lending.borrower_id == current_user.id,
        Lending.is_active == True
    ).all()
    return records

@router.get("/lent", response_model=List[LendingResponse])
def get_lent_books(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    records = db.query(Lending).filter(
        Lending.lender_id == current_user.id,
        Lending.is_active == True
    ).all()
    return records
