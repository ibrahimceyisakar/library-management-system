from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from app.utils.auth import (
    get_current_active_user, 
    normal_user_required, 
    admin_required
)

router = APIRouter()

@router.post("/checkouts/", response_model=schemas.Checkout)
async def checkout_book(
    checkout: schemas.CheckoutCreate,
    db: Session = Depends(get_db),
):
    # Check if book exists and is available
    book = db.query(models.Book).filter(models.Book.id == checkout.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.available_quantity <= 0:
        raise HTTPException(status_code=400, detail="Book is not available")
    
    # Create checkout record
    db_checkout = models.Checkout(
        book_id=checkout.book_id,
        patron_id=checkout.patron_id,
        due_date=checkout.due_date or datetime.utcnow() + timedelta(days=14)
    )
    
    # Update book availability
    book.available_quantity -= 1
    
    db.add(db_checkout)
    db.commit()
    db.refresh(db_checkout)
    return db_checkout

@router.post("/checkouts/{checkout_id}/return")
async def return_book(
    checkout_id: int,
    patron_id: int,
    db: Session = Depends(get_db),
):
    checkout = db.query(models.Checkout).filter(
        models.Checkout.id == checkout_id,
        models.Checkout.patron_id == patron_id
    ).first()
    
    if not checkout:
        raise HTTPException(status_code=404, detail="Checkout record not found or not authorized")
    
    if checkout.is_returned:
        raise HTTPException(status_code=400, detail="Book already returned")
    
    # Update checkout record
    checkout.is_returned = True
    checkout.return_date = datetime.utcnow()
    
    # Update book availability
    book = db.query(models.Book).filter(models.Book.id == checkout.book_id).first()
    book.available_quantity += 1
    
    db.commit()
    db.refresh(checkout)
    return {"message": "Book returned successfully"}

@router.get("/admin/checkouts/all", response_model=List[schemas.Checkout])
@admin_required
async def admin_list_all_checkouts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Admin endpoint to list all checkouts across all patrons.
    Supports pagination via skip and limit parameters.
    """
    checkouts = db.query(models.Checkout).offset(skip).limit(limit).all()
    return checkouts

@router.get("/admin/checkouts/overdue", response_model=List[schemas.Checkout])
@admin_required
async def admin_list_all_overdue_checkouts(
    db: Session = Depends(get_db),
):
    """
    Admin endpoint to list all overdue checkouts across all patrons.
    """
    current_time = datetime.utcnow()
    overdue_checkouts = db.query(models.Checkout).filter(
        models.Checkout.due_date < current_time,
        models.Checkout.is_returned == False
    ).all()
    return overdue_checkouts
