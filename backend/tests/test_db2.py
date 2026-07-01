from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.lending import Lending
from app.models.user import User
from app.models.book import Book
from app.schemas.lending import LendingResponse

engine = create_engine("postgresql://abhi:@localhost/booknest")
Session = sessionmaker(bind=engine)
db = Session()

# Create a test lending
u1 = db.query(User).first()
if not u1:
    u1 = User(name="Test1", email="t1@t.com", password_hash="hash")
    db.add(u1)
u2 = db.query(User).filter(User.id != u1.id).first()
if not u2:
    u2 = User(name="Test2", email="t2@t.com", password_hash="hash")
    db.add(u2)
db.commit()

b = db.query(Book).first()
if not b:
    b = Book(title="Book", author="A", isbn="1", owner_id=u1.id, status="WANT_TO_READ")
    db.add(b)
db.commit()

lend = Lending(book_id=b.id, lender_id=u1.id, borrower_id=u2.id)
db.add(lend)
db.commit()
db.refresh(lend)

try:
    res = LendingResponse.model_validate(lend)
    print("Serialization Successful!")
    print(res.model_dump_json())
except Exception as e:
    print("Serialization Failed:", e)

# Clean up
db.delete(lend)
db.commit()

