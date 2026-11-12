import sqlite3
from pathlib import Path
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

DB_PATH = Path("artifacts/history.db")
DB_PATH.parent.mkdir(exist_ok=True)

# Security Settings
SECRET_KEY = "super-secret-heartsense-key-change-this-in-prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    # Predictions table
    conn.execute(
        """CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction INTEGER NOT NULL,
            p0 REAL NOT NULL,
            p1 REAL NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )"""
    )
    # USERS table (Notice the email and password_hash columns)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )"""
    )
    conn.commit()
    conn.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception

# --- RESTORED THIS FUNCTION SO PREDICT.PY DOES NOT CRASH ---
def log_prediction(prediction: int, p0: float, p1: float):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO predictions (prediction, p0, p1) VALUES (?, ?, ?)",
        (prediction, p0, p1),
    )
    conn.commit()
    conn.close()