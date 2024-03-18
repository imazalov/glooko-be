from fastapi.testclient import TestClient
from main import app, get_db  # Ensure this matches the structure of your project
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base  # Adjust import to match your project structure
import models

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_database.db"  # Example for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_user():
    # Test creating a new user
    response = client.post(
        "/createUser/",
        json={
            "email": "test2@example.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test2@example.com"
    assert "id" in data

def test_create_existing_user():
    # Test trying to create a user with an already registered email
    response = client.post(
        "/createUser/",
        json={
            "email": "test@example.com",
            "password": "anotherpassword",
            "first_name": "Another",
            "last_name": "User"
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"
