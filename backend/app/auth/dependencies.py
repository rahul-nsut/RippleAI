from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt import verify_token
from app.db.session import SessionLocal
from app.db.models import User

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_token(credentials.credentials)  # decodes the JWT
    email = payload.get("sub")                      
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user