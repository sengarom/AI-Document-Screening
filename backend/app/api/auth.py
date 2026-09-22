from fastapi import APIRouter, Response, Request, Depends, HTTPException
from pydantic import BaseModel
from app.core.auth import authenticate_user, create_session, get_current_user, SESSIONS, UserOut

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(request: LoginRequest, response: Response):
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    session_id = create_session(user["id"])
    
    # Set HTTP-only cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=False, # Set to True in production HTTPS
        max_age=86400 # 1 day
    )
    return {"message": "Logged in successfully"}

@router.post("/logout")
def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id and session_id in SESSIONS:
        del SESSIONS[session_id]
    
    response.delete_cookie("session_id")
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserOut)
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "role": current_user["role"],
        "authenticated": True
    }
