# Created: Dec 15, 20:00
# Ver 1.1
# session management
# emegency update
# Changelog: Dec 18 21:00, Added essential calling functions related to personal information
# Jan 3, 20:30, add offset calls to the backend

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from app.models.user import UserResponse, UserUpdate
from app.database import users_collection, scores_collection, difficulties_collection, beatmaps_collection
from app.utils.security import get_current_user, get_optional_user
from app.utils.ep_calculator import calculate_potential
import uuid

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
                "rank": rank,
                "offset": current_user.get("offset", 0.0),
            }
        }
    return {"authenticated": False, "user": None}

# Jiarui Li: personal information display -> return essential information
@router.get("/api/users/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    all_users = list(users_collection.find().sort("ep", -1))
    rank = next((i + 1 for i, u in enumerate(all_users) if u["uid"] == current_user["uid"]), 0)
    return UserResponse(
        uid=current_user["uid"],
        username=current_user["username"],
        avatar=current_user.get("avatar"),
        ep=current_user.get("ep", 0.0),
        rank=rank,
        offset=current_user.get("offset", 0.0),
    )



@router.get("/api/users/{uid}", response_model=UserResponse)
def get_user(uid: str):
    user = users_collection.find_one({"uid": uid})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    all_users = list(users_collection.find().sort("ep", -1))
    rank = next((i + 1 for i, u in enumerate(all_users) if u["uid"] == uid), 0)
    return UserResponse(
        uid=user["uid"],
        username=user["username"],
        avatar=user.get("avatar"),
        ep=user.get("ep", 0.0),
        rank=rank,
        offset=user.get("offset", 0.0),
        flag=user.get("flag", None)
    )


# Jiarui Li: update personal information (player name)
@router.put("/api/users/me")
def update_me(update: UserUpdate, current_user: dict = Depends(get_current_user)):
    update_data = {}
    # Handle both username and offset updates incrementally
    if update.username:
        existing = users_collection.find_one({"username": update.username})
        if existing and existing["uid"] != current_user["uid"]:
            raise HTTPException(status_code=400, detail="Username already taken")
        update_data["username"] = update.username
    if update.offset is not None:
        update_data["offset"] = update.offset

    if update_data:
        users_collection.update_one({"uid": current_user["uid"]}, {"$set": update_data})
    return {"message": "Updated"}


# Jiarui Li: update personal information (avatar)
@router.post("/api/users/me/avatar")
async def upload_avatar(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    ext = file.filename.split(".")[-1]
    filename = f"{current_user['uid']}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = f"app/uploads/avatars/{filename}"

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    avatar_url = f"/uploads/avatars/{filename}"
    users_collection.update_one({"uid": current_user["uid"]}, {"$set": {"avatar": avatar_url}})
    return {"avatar": avatar_url}

# Jiarui Li: fetch basic information related to a specific score
@router.get("/api/users/{uid}/scores")
def get_user_scores(uid: str):
    user = users_collection.find_one({"uid": uid})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_scores = list(scores_collection.find({"uid": uid}))
    best_by_bid = {}
    for s in user_scores:
        bid = s["bid"]
        if bid not in best_by_bid or s["score"] > best_by_bid[bid]["score"]:
            best_by_bid[bid] = s

    result = []
    for s in best_by_bid.values():
        diff = difficulties_collection.find_one({"bid": s["bid"]})
        if diff:
            beatmap = beatmaps_collection.find_one({"sid": diff["sid"]})
            pot = calculate_potential(s["score"], diff["level"])
            result.append({
                "scid": s["scid"],
                "bid": s["bid"],
                "title": beatmap["title"] if beatmap else "Unknown",
                "artist": beatmap["artist"] if beatmap else "Unknown",
                "difficulty_name": diff["name"],
                "difficulty_level": diff["level"],
                "score": s["score"],
                "accuracy": s["accuracy"],
                "rank": s["rank"],
                "potential": pot
            })

    result.sort(key=lambda x: x["potential"], reverse=True)
    return result[:50]


# Jiarui Li: fetch all personal score sorted with EP
@router.get("/api/users/rankings/all")
def get_rankings():
    all_users = list(users_collection.find().sort("ep", -1))
    result = []
    for i, u in enumerate(all_users):
        result.append({
            "rank": i + 1,
            "uid": u.get("uid"),
            "username": u.get("username"),
            "avatar": u.get("avatar"),
            "ep": u.get("ep", 0.0)
        })
    return result