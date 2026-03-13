from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db.session import SessionLocal
from app.db.models import User
from app.auth.hashing import hash_password, verify_password
from app.auth.jwt import create_access_token

router = APIRouter()

class SignupRequest(BaseModel):
    full_name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/signup")
def signup(request: SignupRequest):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == request.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user = User(
            full_name=request.full_name,
            email=request.email,
            hashed_password=hash_password(request.password),
            confluence_spaces=["RAHUL SOOTA"],
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        token = create_access_token({"sub": user.email})
        return {"access_token": token, "token_type": "bearer", "full_name": user.full_name}
    finally:
        db.close()

@router.post("/login")
def login(request: LoginRequest):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == request.email).first()
        if not user or not verify_password(request.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        token = create_access_token({"sub": user.email})
        return {"access_token": token, "token_type": "bearer", "full_name": user.full_name}
    finally:
        db.close()