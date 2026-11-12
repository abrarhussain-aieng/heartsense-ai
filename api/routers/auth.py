from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from api.deps import get_password_hash, verify_password, create_access_token, get_current_user, init_db
import sqlite3
from api.deps import DB_PATH

router = APIRouter(tags=["auth"])

class UserAuth(BaseModel):
    email: str
    password: str
    name: str = ""

@router.post("/register")
def register(user: UserAuth):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password and save
    hashed_pw = get_password_hash(user.password)
    name = user.name if user.name else user.email.split("@")[0]
    
    cursor.execute(
        "INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)",
        (user.email, name, hashed_pw)
    )
    conn.commit()
    conn.close()
    
    return {"message": "User created successfully"}

@router.post("/login")
def login(user: UserAuth):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, name FROM users WHERE email = ?", (user.email,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or not verify_password(user.password, row[0]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create Token
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer", "name": row[1]}

@router.get("/me")
def read_users_me(current_user: str = Depends(get_current_user)):
    return {"email": current_user}