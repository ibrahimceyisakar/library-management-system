from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# Book Schemas
class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    quantity: int = 1

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    available_quantity: int

    class Config:
        from_attributes = True

# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str

# Patron Schemas
class PatronBase(BaseModel):
    name: str
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False

class PatronCreate(PatronBase):
    password: str

class PatronUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class Patron(PatronBase):
    id: int
    membership_date: datetime

    class Config:
        from_attributes = True

# Checkout Schemas
class CheckoutBase(BaseModel):
    book_id: int
    patron_id: int
    due_date: datetime

class CheckoutCreate(CheckoutBase):
    pass

class Checkout(CheckoutBase):
    id: int
    checkout_date: datetime
    return_date: Optional[datetime] = None
    is_returned: bool

    class Config:
        from_attributes = True

# Response Schemas
class BookWithCheckouts(Book):
    checkouts: List[Checkout] = []

class PatronWithCheckouts(Patron):
    checkouts: List[Checkout] = []
