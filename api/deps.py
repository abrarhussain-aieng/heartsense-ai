import sqlite3
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from heartsense.config import settings

DB_PATH = Path("artifacts/history.db")
DB_PATH.parent.mkdir(exist_ok=True)

# Initialize Firebase Admin SDK
# Assumes firebase-service-account.json is in the root directory
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("firebase-service-account.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Warning: Could not initialize Firebase Admin SDK: {e}")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/firebase")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction INTEGER NOT NULL,
            p0 REAL NOT NULL,
            p1 REAL NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            firebase_uid TEXT UNIQUE,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )"""
    )
    conn.commit()
    conn.close()

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        email = decoded_token.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Email not found in token")
        return email
    except firebase_auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

def get_or_create_firebase_user(email: str, name: str, uid: str):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if user:
        if not user[3]:
            cursor.execute("UPDATE users SET firebase_uid = ? WHERE email = ?", (uid, email))
            conn.commit()
    else:
        cursor.execute(
            "INSERT INTO users (email, name, firebase_uid) VALUES (?, ?, ?)",
            (email, name, uid)
        )
        conn.commit()
        
    cursor.execute("SELECT email, name FROM users WHERE email = ?", (email,))
    res = cursor.fetchone()
    conn.close()
    return {"email": res[0], "name": res[1] if res[1] else res[0]}

def log_prediction(prediction: int, p0: float, p1: float):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO predictions (prediction, p0, p1) VALUES (?, ?, ?)",
        (prediction, p0, p1),
    )
    conn.commit()
    conn.close()