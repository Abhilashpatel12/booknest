from fastapi import APIRouter, Depends, HTTPException, status
from app.models import User, Book, Shelf, BookStatus, Lending, Activity, ShelfShare, ShareRole
from app.schemas import BookCreate, BookResponse, BookUpdate, ShelfCreate, ShelfResponse, ShelfUpdate, LendBookRequest, LendingResponse, ShareShelfRequest, UpdateRoleRequest, SharedUserResponse, SignupRequest, LoginRequest, RefreshTokenRequest
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.jwt_handler import create_access_token, create_refresh_token, verify_access_token
from app.core.dependencies import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
import bcrypt

router = APIRouter()

@router.post("/signup")
def signup(user: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        return {"message":"email already exists"}

    hashed_password = bcrypt.hashpw(
        user.password.encode(),
        bcrypt.gensalt()
    ).decode()

    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm=Depends(), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == form_data.username).first()
    
    if existing_user is None:
        raise HTTPException(
            status_code =status.HTTP_401_UNAUTHORIZED,
            detail ="Invalid email or password"
        )
        
    if not bcrypt.checkpw(
        form_data.password.encode(),
        existing_user.password_hash.encode()
    ):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail ="Invalid email or password"
        )    

    access_token = create_access_token(
        data ={"sub":str(existing_user.id)}
    )
    refresh_token = create_refresh_token(
        data ={"sub":str(existing_user.id)}
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type":"bearer"
    }


@router.get("/me")
def get_me(current_user = Depends(get_current_user)):
    return current_user

@router.post("/refresh")
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = verify_access_token(request.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
        
    new_access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }
