import secrets
import hashlib
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Depends
from pydantic import BaseModel

# --- Simple User Store ---
# Hash passwords for demo (using SHA-256 for simplicity without external dependencies)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

DEMO_USERS = {
    "admin@example.com": {
        "id": "admin-1",
        "email": "admin@example.com",
        "password_hash": hash_password("Admin@123"),
        "role": "ADMIN"
    },
    "user@example.com": {
        "id": "user-1",
        "email": "user@example.com",
        "password_hash": hash_password("User@123"),
        "role": "USER"
    }
}

# --- Simple Session Store ---
# session_id -> user_id
SESSIONS: Dict[str, str] = {}

class UserOut(BaseModel):
    id: str
    email: str
    role: str

def authenticate_user(email: str, password: str) -> Optional[dict]:
    user = DEMO_USERS.get(email)
    if user and user["password_hash"] == hash_password(password):
        return user
    return None

def create_session(user_id: str) -> str:
    session_id = secrets.token_urlsafe(32)
    SESSIONS[session_id] = user_id
    return session_id

def get_current_user(request: Request) -> dict:
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in SESSIONS:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = SESSIONS[session_id]
    # Find user by id
    for user in DEMO_USERS.values():
        if user["id"] == user_id:
            return user
            
    raise HTTPException(status_code=401, detail="User not found")

def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user
