# Created: Dec 13 18:10
# Version 1.1
# Encrypt/Dectypt passwords and session management
# Changelog:
# Dec 15 20:00 Added session token decoder

from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from backend.app.config import settings
from backend.app.database import users_collection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Yiwen Wang: hash encrypt/decrypt for login
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Yiwen Wang: use token to preserve session with expired time of 30 days
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# use token to find person
def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    uid = payload.get("uid")

    user = users_collection.find_one({"uid": uid})
    return user

# Yiwen Wang: session token decoder
def get_optional_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    uid = payload.get("uid")
    if uid:
        return users_collection.find_one({"uid": uid})
    return None