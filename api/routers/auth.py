from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from firebase_admin import auth as firebase_auth
from api.deps import get_or_create_firebase_user, get_current_user
import firebase_admin
from firebase_admin import auth, credentials

router = APIRouter(tags=["auth"])

class FirebaseAuthRequest(BaseModel):
    id_token: str

@router.post("/firebase")
async def firebase_login(req: FirebaseAuthRequest): # <--- Name changed from firebase_auth to firebase_login
    try:
        decoded_token = firebase_auth.verify_id_token(req.id_token)
        email = decoded_token.get("email")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not found in token")
            
        name = decoded_token.get("name", email.split("@")[0])
        uid = decoded_token["uid"]
        
        user = get_or_create_firebase_user(email=email, name=name, uid=uid)
        return {"email": user["email"], "name": user["name"]}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Firebase token: {str(e)}")

@router.get("/me")
def read_users_me(current_user: str = Depends(get_current_user)):
    return {"email": current_user}