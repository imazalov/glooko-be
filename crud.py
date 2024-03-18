from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email=email)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


def delete_user(db: Session, user_id: int):
    delete_user = db.query(models.User).filter(models.User.id ==user_id).first()
    if delete_user is None:
        return None
    db.delete(delete_user)
    db.commit()
    return delete_user


def update_user_role(db: Session, user_id: int, new_role: schemas.UserRole):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.role = new_role
        db.commit()
        db.refresh(db_user)
        return db_user
    return None


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session):
    return db.query(models.User).all()



# CRUD operations for Book
def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def update_book(db: Session, book_id: int, book_update: schemas.BookCreate):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book is None:
        return None
    for var, value in vars(book_update).items():
        setattr(db_book, var, value) if value else None
    db.commit()
    db.refresh(db_book)
    return db_book

def delete_book(db: Session, book_id: int):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book is None:
        return None
    db.delete(db_book)
    db.commit()
    return db_book

def get_books(db: Session):
    return db.query(models.Book).all()


def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()


def get_book_by_name(db: Session, book_name: str):
    return db.query(models.Book).filter(models.Book.name == book_name).first()



# CRUD operations for BorrowBook
def borrow_book(db: Session, user_id: int, book_id: int):
    borrow_record = models.BorrowedBook(user_id=user_id, book_id=book_id)
    db.add(borrow_record)
    db.commit()
    db.refresh(borrow_record)
    return borrow_record

def get_borrowed_books_by_user(db: Session, user_id: int):
    return db.query(models.Book).join(
        models.BorrowedBook, models.BorrowedBook.book_id == models.Book.id
    ).filter(models.BorrowedBook.user_id == user_id).all()


def delete_borrowed_book(db: Session, user_id: int, book_id: int) -> bool:
    # Directly target the entry with both user_id and book_id
    affected_rows = db.query(models.BorrowedBook).filter(
        models.BorrowedBook.user_id == user_id,
        models.BorrowedBook.book_id == book_id
    ).delete(synchronize_session=False)

    if affected_rows > 0:
        db.commit()
        return True
    return False

