from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, engine
import crud, models, schemas
from crud import authenticate_user
from jose import jwt

# The rest of your FastAPI app setup
SECRET_KEY = "glooko"
ALGORITHM = "HS256"
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # The origin of your React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dp_dependency = Annotated[Session,Depends(get_db())]
models.Base.metadata.create_all(bind=engine)
# Dependency for authorization (you'll need to implement these functions)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    # Use token to authenticate and get user
    return {}

@app.get("/")
def read_root():
    return {"message": "Welcome to the bookstore API!"}

@app.post("/login")
def login(login_details: schemas.LoginSchema, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_details.email, login_details.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    # Here you would generate a JWT token or another form of authentication token
    # Generate a JWT token here
    token_data = {"sub": user.email, "id": user.id, "role": user.role.value}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return { "token": token,
             "role": user.role.value ,
             "userId": user.id}
# User endpoints
@app.post("/createUser/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.User])
def list_users(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/email/{email}", response_model=schemas.User)
def read_user(email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.put("/users/{user_id}/role", response_model=schemas.User)
def update_role(user_id: int, role_update: schemas.UserRoleUpdate, db: Session = Depends(get_db)):

    updated_user = crud.update_user_role(db, user_id=user_id, new_role=role_update.role)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@app.delete("/users/delete/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session =Depends(get_db)):
    return crud.delete_user(db, user_id=user_id)

# Books endpoints

@app.post("/addBook/", response_model=schemas.BookCreate)
def create_book_endpoint(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return crud.create_book(db=db, book=book)


@app.get("/books/", response_model=List[schemas.BookRead])
def read_books(db: Session = Depends(get_db)):
    books = crud.get_books(db)
    return books


@app.get("/books/{book_id}", response_model=schemas.BookRead)
def read_book(book_id: int, db: Session = Depends(get_db)):
    db_book = crud.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.put("/books/{book_id}", response_model=schemas.BookCreate)
def update_book_endpoint(book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db)):
    updated_book = crud.update_book(db, book_id=book_id, book_update=book)
    if updated_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book


@app.delete("/books/{book_id}", response_model=schemas.BookRead)
def delete_book_endpoint(book_id: int, db: Session = Depends(get_db)):
    db_book = crud.delete_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.post("/users/{user_id}/addBook")
def add_book_to_user(book_details: schemas.BookCreate, user_id: int, db: Session = Depends(get_db)):
    # Check if book exists, if not create it
    book = crud.get_book_by_name(db, book_name=book_details.name)
    if not book:
        book = crud.create_book(db=db, book=book_details)
    # Now, associate the book with the user
    return crud.borrow_book(db=db, user_id=user_id, book_id=book.id)

# BorrowBook endpoints
@app.post("/users/{user_id}/borrowBook/{book_id}", response_model=schemas.BorrowedBookCreate)
def borrowBook_to_user(user_id: int, book_id: int, db: Session = Depends(get_db)):
    return crud.borrow_book(db=db, user_id=user_id, book_id=book_id)

@app.post("/borrowBook/")
def borrow_book_endpoint(user_id: int, book_id: int, db: Session = Depends(get_db)):
    # You might want to add checks here to ensure both the user and book exist
    borrow_record = crud.borrow_book(db=db, user_id=user_id, book_id=book_id)
    return {"message": "Book borrowed successfully"}

@app.get("/users/{user_id}/borrowed_books", response_model=List[schemas.BorrowedBookInfo])
def read_borrowed_books(user_id: int, db: Session = Depends(get_db)):
    borrowed_books = crud.get_borrowed_books_by_user(db, user_id=user_id)
    if not borrowed_books:
        raise HTTPException(status_code=404, detail="No borrowed books found for this user")
    return [{"book_id": book.id, "name": book.name} for book in borrowed_books]

@app.delete("/users/{user_id}/delete/borrowed_books/{book_id}", status_code=204)
def delete_borrowed_book(user_id: int, book_id: int, db: Session = Depends(get_db)):
    # You might want to include authentication and authorization checks here
    if not crud.delete_borrowed_book(db, user_id=user_id, book_id=book_id):
        raise HTTPException(status_code=404, detail="Borrowed book not found")
    return {"detail": "Borrowed book deleted"}
