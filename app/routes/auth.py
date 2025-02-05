from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models import models
from app.schemas import schemas as user_schemas
from app.utils.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_active_user,
    get_current_superuser
)

router = APIRouter()

@router.post("/token", response_model=user_schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.Patron).filter(models.Patron.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users/", response_model=user_schemas.Patron)
async def create_user(
    user: user_schemas.PatronCreate,
    db: Session = Depends(get_db),
    current_user: models.Patron = Depends(get_current_superuser)
):
    db_user = db.query(models.Patron).filter(models.Patron.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = db.query(models.Patron).filter(models.Patron.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = models.Patron(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        is_active=user.is_active,
        is_superuser=user.is_superuser
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/me/", response_model=user_schemas.Patron)
async def read_users_me(current_user: models.Patron = Depends(get_current_active_user)):
    return current_user

@router.put("/users/me/", response_model=user_schemas.Patron)
async def update_user_me(
    user: user_schemas.PatronUpdate,
    current_user: models.Patron = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if user.email:
        db_user = db.query(models.Patron).filter(models.Patron.email == user.email).first()
        if db_user and db_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = user.email
    
    if user.username:
        db_user = db.query(models.Patron).filter(models.Patron.username == user.username).first()
        if db_user and db_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Username already registered")
        current_user.username = user.username
    
    if user.password:
        current_user.hashed_password = get_password_hash(user.password)
    
    db.commit()
    db.refresh(current_user)
    return current_user
