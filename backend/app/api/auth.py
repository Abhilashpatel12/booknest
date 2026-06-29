from fastapi import APIRouter
from app.core.database import cursor, conn
from app.schemas.user import SignupRequest, LoginRequest
import bcrypt

router = APIRouter()

@router.post("/signup")
def signup(user: SignupRequest):
    cursor.execute(
        "SELECT * FROM users WHERE email = %s",
        (user.email,)
    )
    existing_user = cursor.fetchone()

    if existing_user:
        return {"message":"email already exists"}

    hashed_password = bcrypt.hashpw(
        user.password.encode(),
        bcrypt.gensalt()
    ).decode()

    cursor.execute(
        """
        INSERT INTO users (name, email, password_hash)
        VALUES (%s, %s, %s)
        """,
        (user.name, user.email, hashed_password)
    )

    conn.commit()

    return {"message": "User created successfully"}


@router.post("/login")
def login(user: LoginRequest):
    cursor.execute(
        "SELECT * FROM users WHERE email = %s",
        (user.email,)
    )   
    existing_user = cursor.fetchone()
    if not existing_user:
        return {"message": "Invalid email or password"}
    stored_password = existing_user[3]

    if not bcrypt.checkpw(
        user.password.encode(),
        stored_password.encode()
    ):
        return {"message": "Invalid email or password"}    

    return {"message":"Login success"}
