from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from app.utils.auth import (
    get_db, 
    get_current_active_user, 
    admin_required, 
    normal_user_required
)

router = APIRouter()

@router.post("/books/", response_model=schemas.Book)
@admin_required
async def create_book(
    book: schemas.BookCreate, 
    db: Session = Depends(get_db),
    current_user: models.Patron = Depends(get_current_active_user)
):
    db_book = models.Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        quantity=book.quantity,
        available_quantity=book.quantity
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.get("/books/", response_model=List[schemas.Book])
async def read_books(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.Patron = Depends(get_current_active_user)
):
    books = db.query(models.Book).offset(skip).limit(limit).all()
    return books

@router.get("/books/{book_id}", response_model=schemas.BookWithCheckouts)
async def read_book(
    book_id: int, 
    db: Session = Depends(get_db),
    current_user: models.Patron = Depends(get_current_active_user)
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/books/{book_id}", response_model=schemas.Book)
@admin_required
async def update_book(
    book_id: int, 
    book: schemas.BookCreate, 
    db: Session = Depends(get_db),
    current_user: models.Patron = Depends(get_current_active_user)
):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    for var, value in vars(book).items():
        setattr(db_book, var, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book

@router.delete("/books/{book_id}")
@admin_required
async def delete_book(
    book_id: int, 
    db: Session = Depends(get_db),
    current_user: models.Patron = Depends(get_current_active_user)
):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(db_book)
    db.commit()
    return {"message": "Book deleted successfully"}
