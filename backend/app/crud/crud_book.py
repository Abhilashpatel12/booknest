from typing import Any, Dict, List, Literal, Optional, Union
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.crud.base import CRUDBase
from app.models.book import Book, BookStatus
from app.schemas.book import BookCreate, BookUpdate

class CRUDBook(CRUDBase[Book, BookCreate, BookUpdate]):
    def get_multi_filtered(
        self, 
        db: Session, 
        owner_id: int, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        book_status: Optional[BookStatus] = None,
        search: Optional[str] = None,
        sort_by: Literal["rating", "title", "date_added"] = "date_added"
    ) -> List[Book]:
        query = db.query(self.model).filter(self.model.owner_id == owner_id)
        
        if book_status:
            query = query.filter(self.model.status == book_status)
        if search:
            search_term = f"%{search}%"
            query = query.filter((self.model.title.ilike(search_term) | self.model.author.ilike(search_term)))
            
        if sort_by == "rating":
            query = query.order_by(self.model.rating.desc())
        elif sort_by == "title":
            query = query.order_by(self.model.title.asc())
        else:
            query = query.order_by(self.model.created_at.desc())
            
        return query.offset(skip).limit(limit).all()

    def update(
        self,
        db: Session,
        *,
        db_obj: Book,
        obj_in: Union[BookUpdate, Dict[str, Any]]
    ) -> Book:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        new_total_pages = update_data.get("total_pages", db_obj.total_pages)
        new_current_page = update_data.get("current_page", db_obj.current_page)
        
        if new_current_page < 0:
            raise ValueError("current page cannot be negative")
        if new_current_page > new_total_pages:
            raise ValueError("current page cannot be greater than total pages")
            
        if new_current_page == new_total_pages and new_total_pages > 0:
            update_data["status"] = BookStatus.FINISHED
            update_data["finished_date"] = datetime.now(timezone.utc)
        elif new_current_page < new_total_pages:
            current_status = update_data.get("status", db_obj.status)
            if current_status == BookStatus.FINISHED:
                update_data["status"] = BookStatus.READING
                update_data["finished_date"] = None
            elif current_status == BookStatus.WANT_TO_READ and new_current_page > 0:
                update_data["status"] = BookStatus.READING

        
        return super().update(db, db_obj=db_obj, obj_in=update_data)

book = CRUDBook(Book)
