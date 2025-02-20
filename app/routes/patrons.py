from app.utils.auth import get_password_hash
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()

@router.post("/patrons/", response_model=schemas.Patron)
def create_patron(patron: schemas.PatronCreate, db: Session = Depends(get_db)):
    # Check if the email is already registered
    db_patron = db.query(models.Patron).filter(models.Patron.email == patron.email).first()
    if db_patron:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    hashed_password = get_password_hash(patron.password)
    db_patron = models.Patron(name=patron.name, email=patron.email, hashed_password=hashed_password)
    db.add(db_patron)
    db.commit()
    db.refresh(db_patron)
    return db_patron

@router.get("/patrons/", response_model=List[schemas.Patron])
def read_patrons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    patrons = db.query(models.Patron).offset(skip).limit(limit).all()
    return patrons

@router.get("/patrons/{patron_id}", response_model=schemas.PatronWithCheckouts)
def read_patron(patron_id: int, db: Session = Depends(get_db)):
    patron = db.query(models.Patron).filter(models.Patron.id == patron_id).first()
    if patron is None:
        raise HTTPException(status_code=404, detail="Patron not found")
    return patron

@router.put("/patrons/{patron_id}", response_model=schemas.Patron)
def update_patron(patron_id: int, patron: schemas.PatronCreate, db: Session = Depends(get_db)):
    db_patron = db.query(models.Patron).filter(models.Patron.id == patron_id).first()
    if db_patron is None:
        raise HTTPException(status_code=404, detail="Patron not found")
    
    for var, value in vars(patron).items():
        setattr(db_patron, var, value)
    
    db.commit()
    db.refresh(db_patron)
    return db_patron

@router.delete("/patrons/{patron_id}")
def delete_patron(patron_id: int, db: Session = Depends(get_db)):
    db_patron = db.query(models.Patron).filter(models.Patron.id == patron_id).first()
    if db_patron is None:
        raise HTTPException(status_code=404, detail="Patron not found")
    
    db.delete(db_patron)
    db.commit()
    return {"message": "Patron deleted successfully"}
