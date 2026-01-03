from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    offset: Optional[float] = None

# Jiarui Li: we add the offset to save to the mongodb backend
class UserResponse(BaseModel):
    uid: str
    username: str
    avatar: Optional[str] = None
    # Jiarui Li: added personal EP calculation
    ep: float = 0.0
    offset: float = 0.0
    rank: int = 0