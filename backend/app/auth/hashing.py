#hashing and verifying passwords
from passlib.context import CryptContext

passw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return passw_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return passw_context.verify(password, hashed_password)

def get_password_hash(password: str) -> str:
    return hash_password(password)