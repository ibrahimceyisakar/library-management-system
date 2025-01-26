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

# Patron Schemas
class PatronBase(BaseModel):
    name: str
    email: EmailStr

class PatronCreate(PatronBase):
    pass

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
