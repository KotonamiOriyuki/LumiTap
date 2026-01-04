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

class UserResponse(BaseModel):
    uid: str
    username: str
    avatar: Optional[str] = None
    # Jiarui Li: added personal EP calculation
    ep: float = 0.0
    rank: int = 0
    offset: float = 0.0
    # Cheng Wang: added administration functionality
    flag: Optional[str] = None