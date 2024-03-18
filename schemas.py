from typing import List, Union
from pydantic import BaseModel, EmailStr
from models import UserRole

# User schema
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    first_name: str
    last_name: str

class User(UserBase):
    first_name: str
    last_name: str
    id: int
    role: UserRole
    books: List[int] = []

    class Config:
        from_attributes = True

class UserRoleUpdate(BaseModel):
    role: UserRole
class BookBase(BaseModel):
    name: str

class BookCreate(BookBase):
    pass

class BookRead(BookBase):
    id: int

    class Config:
        from_attributes = True

class BorrowedBook(BaseModel):
    user_id: int
    book_id: int

class BorrowedBookInfo(BaseModel):
    book_id: int
    name: str

    class Config:
        from_attributes = True
class BorrowedBookCreate(BorrowedBook):
    pass

class BorrowedBookRead(BorrowedBook):
    id: int

    class Config:
        from_attributes = True


class LoginSchema(BaseModel):
    email: str
    password: str