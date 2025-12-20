# Created: Dec 13 19:10
# Version 1.1
# API Calls related to authentication
# Changelog: Dec 18, 20:00 Added EP initialization of personal data

from fastapi import APIRouter, HTTPException, Response
from backend.app.models.user import UserCreate, UserLogin, UserResponse
from backend.app.database import users_collection
from backend.app.utils.security import hash_password, verify_password, create_access_token
import uuid

router = APIRouter()

# Yiwen Wang: User reg
@router.post("/api/auth/register", response_model=UserResponse)
def register(user: UserCreate, response: Response):
    # Yiwen Wang: Check duplicate username
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")

    uid = str(uuid.uuid4())[:8]
    while users_collection.find_one({"uid": uid}):
        uid = str(uuid.uuid4())[:8]

    user_doc = {
        "uid": uid,
        "username": user.username,
        "password": hash_password(user.password),
        "avatar": None,
    #     Jiarui Li: EP Display
        "ep": 0.0
    }
    users_collection.insert_one(user_doc)

    token = create_access_token({"uid": uid})
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=30 * 24 * 60 * 60)

    return UserResponse(uid=uid, username=user.username, avatar=None)


# Yiwen Wang: Login and verify password
@router.post("/api/auth/login", response_model=UserResponse)
def login(user: UserLogin, response: Response):
    db_user = users_collection.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"uid": db_user["uid"]})
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=30 * 24 * 60 * 60)
    # Jiarui Li: newly added
    all_users = list(users_collection.find().sort("ep", -1))
    rank = next((i + 1 for i, u in enumerate(all_users) if u.get("uid") == db_user["uid"]), 0)

    return UserResponse(
        uid=db_user["uid"],
        username=db_user["username"],
        avatar=db_user.get("avatar"),
    #     Jiarui Li: EP Display
        ep=db_user.get("ep", 0.0),
        rank=rank
    )


@router.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out"}