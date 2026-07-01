from app.core.dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends
from app.models import User, Book, Shelf, BookStatus, Lending, Activity, ShelfShare, ShareRole
from app.models.associations import book_shelf_association
from app.schemas import BookCreate, BookResponse, BookUpdate, ShelfCreate, ShelfResponse, ShelfUpdate, LendBookRequest, LendingResponse, ShareShelfRequest, UpdateRoleRequest, SharedUserResponse, SignupRequest, LoginRequest, RefreshTokenRequest
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_books = db.query(func.count(Book.id)).filter(Book.owner_id == current_user.id).scalar() or 0
    reading = db.query(func.count(Book.id)).filter(Book.owner_id == current_user.id, Book.status == BookStatus.READING).scalar() or 0
    
    current_year = datetime.now().year
    finished = db.query(func.count(Book.id)).filter(
        Book.owner_id == current_user.id, 
        Book.status == BookStatus.FINISHED,
        extract('year', Book.finished_date) == current_year
    ).scalar() or 0
    
    want_to_read = db.query(func.count(Book.id)).filter(Book.owner_id == current_user.id, Book.status == BookStatus.WANT_TO_READ).scalar() or 0
    total_pages_read = db.query(func.sum(Book.current_page)).filter(Book.owner_id == current_user.id).scalar() or 0
    avg_rating = db.query(func.avg(Book.rating)).filter(Book.owner_id == current_user.id, Book.rating != None).scalar() or 0.0
    books_lent = db.query(func.count(Lending.id)).filter(Lending.lender_id == current_user.id, Lending.is_active == True).scalar() or 0
    
    most_populated_shelf = db.query(Shelf).filter(Shelf.owner_id == current_user.id).outerjoin(book_shelf_association).group_by(Shelf.id).order_by(func.count(book_shelf_association.c.book_id).desc()).first()
    most_populated_shelf_name = most_populated_shelf.name if most_populated_shelf else None
    
    shelves_shared_with_me = db.query(func.count(ShelfShare.id)).filter(ShelfShare.user_id == current_user.id).scalar() or 0
    
    recent_activity = db.query(Activity).filter(Activity.user_id == current_user.id).order_by(Activity.timestamp.desc()).limit(5).all()

    return {
        "total_books": total_books,
        "reading": reading,
        "finished_this_year": finished,
        "want_to_read": want_to_read,
        "total_pages_read": total_pages_read,
        "average_rating": round(avg_rating, 1) if avg_rating else 0.0,
        "shelf_with_most_books": most_populated_shelf_name,
        "shelves_shared_with_me": shelves_shared_with_me,
        "books_currently_lent": books_lent,
        "recent_activity": [
            {
                "action": act.action_type,
                "description": act.description,
                "timestamp": act.timestamp
            } for act in recent_activity
        ]
    }
