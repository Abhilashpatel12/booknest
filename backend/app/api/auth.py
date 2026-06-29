from fastapi import APIRouter,Depends,HTTPException,status
from app.core.database import cursor, conn
from app.schemas.user import SignupRequest, LoginRequest
from app.core.jwt_handler import create_access_token
from app.core.dependencies import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
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
def login(form_data: OAuth2PasswordRequestForm=Depends()):
    cursor.execute(
        "SELECT * FROM users WHERE email = %s",
        (form_data.username,)
    )   
    existing_user = cursor.fetchone()
    if existing_user is None:
        raise HTTPException(
            status_code =status.HTTP_401_UNAUTHORIZED,
            detail ="Invalid email or password"
        )
    if not bcrypt.checkpw(
        form_data.password.encode(),
        existing_user["password_hash"].encode()
    ):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail ="Invalid email or password"
        )    

    acess_token = create_access_token(
        data ={"sub":str(existing_user["id"])}
    )  
    return {
        "access_token":acess_token,
        "token_type":"bearer"
    }  


@router.get("/me")
def get_me(current_user = Depends(get_current_user)):
    return current_user
