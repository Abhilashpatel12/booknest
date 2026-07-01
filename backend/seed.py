import sys
import os

# Add the backend directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import bcrypt
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.book import Book, BookStatus
from app.models.shelf import Shelf
from app.models.sharing import ShelfShare, ShareRole
from app.models.lending import Lending

def seed_db():
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 1. Create two test users
        print("Creating users...")
        pwd1 = bcrypt.hashpw("password123".encode(), bcrypt.gensalt()).decode()
        pwd2 = bcrypt.hashpw("password123".encode(), bcrypt.gensalt()).decode()
        
        user1 = db.query(User).filter(User.email == "alice@example.com").first()
        if not user1:
            user1 = User(name="Alice Test", email="alice@example.com", password_hash=pwd1)
            db.add(user1)
            
        user2 = db.query(User).filter(User.email == "bob@example.com").first()
        if not user2:
            user2 = User(name="Bob Test", email="bob@example.com", password_hash=pwd2)
            db.add(user2)
            
        db.commit()
        db.refresh(user1)
        db.refresh(user2)
        
        # 2. Create sample books
        print("Creating books...")
        book1 = db.query(Book).filter(Book.title == "Alice's First Book").first()
        if not book1:
            book1 = Book(owner_id=user1.id, title="Alice's First Book", author="Author A", total_pages=300, status=BookStatus.FINISHED)
            db.add(book1)
            
        book2 = db.query(Book).filter(Book.title == "Bob's Guide to Lending").first()
        if not book2:
            book2 = Book(owner_id=user2.id, title="Bob's Guide to Lending", author="Author B", total_pages=200, status=BookStatus.READING)
            db.add(book2)
            
        db.commit()
        db.refresh(book1)
        db.refresh(book2)
        
        # 3. Create shelves and associate books
        print("Creating shelves...")
        shelf1 = db.query(Shelf).filter(Shelf.name == "Alice's Favorites").first()
        if not shelf1:
            shelf1 = Shelf(owner_id=user1.id, name="Alice's Favorites")
            db.add(shelf1)
            db.commit()
            db.refresh(shelf1)
            shelf1.books.append(book1)
            db.commit()
            
        shelf2 = db.query(Shelf).filter(Shelf.name == "Bob's Reading List").first()
        if not shelf2:
            shelf2 = Shelf(owner_id=user2.id, name="Bob's Reading List")
            db.add(shelf2)
            db.commit()
            db.refresh(shelf2)
            shelf2.books.append(book2)
            db.commit()
            
        # 4. Share shelves
        print("Sharing shelves...")
        share1 = db.query(ShelfShare).filter(ShelfShare.shelf_id == shelf1.id, ShelfShare.user_id == user2.id).first()
        if not share1:
            # Share Alice's shelf with Bob as viewer
            share1 = ShelfShare(shelf_id=shelf1.id, user_id=user2.id, role=ShareRole.viewer)
            db.add(share1)
            
        share2 = db.query(ShelfShare).filter(ShelfShare.shelf_id == shelf2.id, ShelfShare.user_id == user1.id).first()
        if not share2:
            # Share Bob's shelf with Alice as editor
            share2 = ShelfShare(shelf_id=shelf2.id, user_id=user1.id, role=ShareRole.editor)
            db.add(share2)
            
        db.commit()
        
        # 5. Create an active lending
        print("Creating active lending...")
        lending1 = db.query(Lending).filter(Lending.book_id == book1.id, Lending.borrower_id == user2.id).first()
        if not lending1:
            # Alice lends her book to Bob
            lending1 = Lending(book_id=book1.id, lender_id=user1.id, borrower_id=user2.id, is_active=True)
            db.add(lending1)
            db.commit()

        print("Seed data successfully created!")
        print(f"Users created:\n- {user1.email} / password123\n- {user2.email} / password123")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
