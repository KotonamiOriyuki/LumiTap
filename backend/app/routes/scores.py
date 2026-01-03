# Created: Dec 15, 20:00
# Ver 1.2
# Responses related to score submitting
# Changelog: Dec 16, 20:00 -> Added EP calculation portal
# Dec 18, 20:30 -> Added leaderboard ranking
# Jan 1, 20:00 -> Transfer the search algorithm to the backend
from fastapi import APIRouter, HTTPException, Depends
from app.models.score import ScoreCreate, ScoreResponse
from app.database import scores_collection, difficulties_collection, users_collection, beatmaps_collection
from app.utils.security import get_current_user
from app.utils.ep_calculator import calculate_user_ep, get_rank_from_accuracy, calculate_potential
from datetime import datetime
import uuid

router = APIRouter()

def lcs_length(s1: str, s2: str) -> int:
    s1, s2 = s1.lower(), s2.lower()
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]

# Jiarui Li: LCS search algorithm
@router.get("/api/beatmaps/search")
def search_beatmaps(q: str = ""):
    all_beatmaps = list(beatmaps_collection.find())
    if not q:
        results = all_beatmaps
    else:
        scored = []
        for b in all_beatmaps:
            title_score = lcs_length(q, b["title"])
            artist_score = lcs_length(q, b["artist"])
            max_score = max(title_score, artist_score)
            if max_score > 0:
                scored.append((max_score, b))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [b for _, b in scored]

    response = []
    for b in results:
        diffs = list(difficulties_collection.find({"sid": b["sid"]}).sort("level", 1))
        uploader = users_collection.find_one({"uid": b["uploader_uid"]})
        response.append({
            "sid": b["sid"],
            "title": b["title"],
            "artist": b["artist"],
            "bpm": b["bpm"],
            "background": b.get("background"),
            "audio": b.get("audio"),
            "uploader_uid": b["uploader_uid"],
            "uploader_name": uploader["username"] if uploader else "Unknown",
            "difficulties": [
                {"bid": d["bid"], "name": d["name"], "level": d["level"], "note_count": d.get("note_count", 0)}
                for d in diffs
            ]
        })
    return response


# Chenxi Liu: submit the existing score
@router.post("/api/scores/submit")
def submit_score(score_data: ScoreCreate, current_user: dict = Depends(get_current_user)):
    diff = difficulties_collection.find_one({"bid": score_data.bid})
    if not diff:
        raise HTTPException(status_code=404, detail="Difficulty not found")

    rank = get_rank_from_accuracy(score_data.accuracy)
    potential = calculate_potential(score_data.score, diff["level"])

    existing = scores_collection.find_one({"uid": current_user["uid"], "bid": score_data.bid})

    scid = str(uuid.uuid4())[:8]
    while scores_collection.find_one({"scid": scid}):
        scid = str(uuid.uuid4())[:8]

    score_doc = {
        "scid": scid,
        "uid": current_user["uid"],
        "bid": score_data.bid,
        "score": score_data.score,
        "accuracy": score_data.accuracy,
        "rank": rank,
        "great_count": score_data.great_count,
        "good_count": score_data.good_count,
        "miss_count": score_data.miss_count,
        "max_combo": score_data.max_combo,
        "potential": potential,
        "created_at": datetime.utcnow()
    }

    if existing:
        if score_data.score > existing["score"]:
            scores_collection.update_one({"scid": existing["scid"]}, {"$set": score_doc})
            scid = existing["scid"]
    else:
        scores_collection.insert_one(score_doc)

    # Rongze Fan: Add ep submission portal to the api
    new_ep = calculate_user_ep(current_user["uid"])
    users_collection.update_one({"uid": current_user["uid"]}, {"$set": {"ep": new_ep}})

    all_scores = list(scores_collection.find({"bid": score_data.bid}).sort("score", -1))
    ranking = next((i + 1 for i, s in enumerate(all_scores) if s["uid"] == current_user["uid"]), 0)

    return {
        "scid": scid,
        "score": score_data.score,
        "accuracy": score_data.accuracy,
        "rank": rank,
        "ranking": ranking,
        "potential": potential
    }


# Zheng Wu: added leaderboard display function of a difficulty
@router.get("/api/scores/leaderboard/{bid}")
def get_leaderboard(bid: str):
    diff = difficulties_collection.find_one({"bid": bid})
    if not diff:
        raise HTTPException(status_code=404, detail="Difficulty not found")

    all_scores = list(scores_collection.find({"bid": bid}).sort("score", -1).limit(100))

    result = []
    for i, s in enumerate(all_scores):
        user = users_collection.find_one({"uid": s["uid"]})
        result.append({
            "position": i + 1,
            "scid": s["scid"],
            "uid": s["uid"],
            "username": user["username"] if user else "Unknown",
            "score": s["score"],
            "accuracy": s["accuracy"],
            "rank": s["rank"]
        })
    return result


# Zheng Wu: this is required for profile to beatmap
@router.get("/api/beatmaps/sid-from-bid/{bid}")
def get_sid_from_bid(bid: str):
    diff = difficulties_collection.find_one({"bid": bid})
    if not diff:
        raise HTTPException(status_code=404, detail="Difficulty not found")
    return {"sid": diff["sid"]}