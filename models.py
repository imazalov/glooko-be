from sqlalchemy.exc import SQLAlchemyError

from database import Base
from sqlalchemy import create_engine, Column, Integer, String, Enum, ForeignKey, Table, MetaData
from sqlalchemy.orm import declarative_base, relationship
import enum


Base = declarative_base()
engine = create_engine('sqlite:///library.db')  # Adjust for your database

class UserRole(enum.Enum):
    admin = "admin"
    librarian = "librarian"
    customer = "customer"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.customer)

    borrowed_books = relationship("BorrowedBook", back_populates="user")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    # Removed the user_id and owner relationship


class BorrowedBook(Base):
    __tablename__ = "borrowed_books"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    user = relationship("User", back_populates="borrowed_books")
    book = relationship("Book")

def update_database(engine):
    metadata = MetaData()
    metadata.reflect(bind=engine)

    if 'borrowed_books' not in metadata.tables:
        # If the borrowed_books table doesn't exist, create all tables
        Base.metadata.create_all(engine)
    else:
        # If you need to update an existing table, you can run custom SQL here.
        # This is just an example to add a column; real logic will depend on your needs
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                # Example: Add a new column if it doesn't exist (SQLite syntax; adjust for other DBMS)
                # conn.execute(text("ALTER TABLE borrowed_books ADD COLUMN new_column INTEGER"))
                trans.commit()
            except SQLAlchemyError as e:
                trans.rollback()
                print(f"Error updating database schema: {e}")

# Make sure relationships are properly initialized
Base.metadata.create_all(engine)

# Update database schema upon startup
update_database(engine)