from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User

engine = create_engine("postgresql://abhi:@localhost/booknest")
Session = sessionmaker(bind=engine)
db = Session()

user = db.query(User).filter(User.email == "abhilashpatel960@gmail.com").first()
if user:
    print(f"User FOUND: ID={user.id}, Name={user.name}, Email={user.email}")
else:
    print("User NOT FOUND")

