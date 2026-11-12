from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import sqlite3
from api.deps import DB_PATH, init_db, get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(tags=["auth"])

class UserAuth(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(user: UserAuth):
    if len(user.username) < 3 or len(user.password) < 4:
        raise HTTPException(status_code=400, detail="Username must be 3+ chars, password 4+ chars.")
    
    init_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO users (username, hashed_password) VALUES (?, ?)",
            (user.username, get_password_hash(user.password))
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        conn.close()
    
    return {"message": "User created successfully"}

@router.post("/login")
def login(user: UserAuth):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT hashed_password FROM users WHERE username = ?", (user.username,))
    row = cursor.fetchone()
    conn.close()

    if not row or not verify_password(user.password, row[0]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def read_users_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}