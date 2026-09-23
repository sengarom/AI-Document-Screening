from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.auth import require_admin, DEMO_USERS, hash_password
import uuid

router = APIRouter()

class UserCreate(BaseModel):
    email: str
    password: str
    role: str

class PasswordUpdate(BaseModel):
    password: str

class StatusUpdate(BaseModel):
    status: str

@router.get("/users")
def get_users(current_user: dict = Depends(require_admin)):
    users = []
    for user in DEMO_USERS.values():
        users.append({
            "user_id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "status": user.get("status", "ACTIVE")
        })
    return users

@router.post("/users")
def create_user(request: UserCreate, current_user: dict = Depends(require_admin)):
    if request.role not in ["USER", "ADMIN"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if request.email in DEMO_USERS:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user_id = str(uuid.uuid4())
    DEMO_USERS[request.email] = {
        "id": user_id,
        "email": request.email,
        "password_hash": hash_password(request.password),
        "role": request.role,
        "status": "ACTIVE"
    }
    
    return {
        "user_id": user_id,
        "email": request.email,
        "role": request.role,
        "status": "ACTIVE"
    }

@router.patch("/users/{user_id}/password")
def update_password(user_id: str, request: PasswordUpdate, current_user: dict = Depends(require_admin)):
    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    for email, user in DEMO_USERS.items():
        if user["id"] == user_id:
            user["password_hash"] = hash_password(request.password)
            return {"message": "Password updated successfully"}
    
    raise HTTPException(status_code=404, detail="User not found")

@router.patch("/users/{user_id}/status")
def update_status(user_id: str, request: StatusUpdate, current_user: dict = Depends(require_admin)):
    if request.status not in ["ACTIVE", "DISABLED"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    if user_id == current_user["id"] and request.status == "DISABLED":
        raise HTTPException(status_code=400, detail="Cannot disable own account")
    
    for email, user in DEMO_USERS.items():
        if user["id"] == user_id:
            user["status"] = request.status
            return {"message": f"User status updated to {request.status}"}
            
    raise HTTPException(status_code=404, detail="User not found")
