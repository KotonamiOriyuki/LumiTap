# Created: Dec 15, 20:00
# Ver 1.0
# session management
# emegency update

from fastapi import APIRouter, HTTPException, Depends
from backend.app.database import users_collection
from backend.app.utils.security import get_optional_user


router = APIRouter()

# Yiwen Wang: Check the session status
@router.get("/api/users/check")
def check_auth(current_user: dict = Depends(get_optional_user)):
    if current_user:
        all_users = list(users_collection.find().sort("ep", -1))
        rank = next((i + 1 for i, u in enumerate(all_users) if u["uid"] == current_user["uid"]), 0)
        return {
            "authenticated": True,
            "user": {
                "uid": current_user["uid"],
                "username": current_user["username"],
                "avatar": current_user.get("avatar"),
                "ep": current_user.get("ep", 0.0),
                "rank": rank
            }
        }
    return {"authenticated": False, "user": None}

