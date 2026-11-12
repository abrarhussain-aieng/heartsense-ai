from fastapi import APIRouter

router = APIRouter(tags=["auth"])

@router.get("/me")
def read_users_me():
    """
    Returns a static user profile since authentication is removed.
    This prevents the frontend from crashing when it asks for user data.
    """
    return {
        "email": "abrar@heartsense.ai", 
        "name": "Abrar Hussain"
    }

@router.post("/login")
def dummy_login():
    """
    A dummy endpoint just in case any old frontend code 
    still tries to hit the login route.
    """
    return {"status": "success", "message": "Access granted."}