# Created: Dec 15, 20:00
# Ver 1.1
# Responses related to score submitting
# Changelog: Dec 16, 20:00 -> Added EP calculation portal
from fastapi import APIRouter, HTTPException, Depends
from backend.app.models.score import ScoreCreate
from backend.app.database import scores_collection, difficulties_collection, users_collection
from backend.app.utils.security import get_current_user
from backend.app.utils.ep_calculator import get_rank_from_accuracy, calculate_user_ep
from datetime import datetime
import uuid

router = APIRouter()

# Chenxi Liu: submit the existing score
@router.post("/api/scores/submit")
def submit_score(score_data: ScoreCreate, current_user: dict = Depends(get_current_user)):
    diff = difficulties_collection.find_one({"bid": score_data.bid})
    if not diff:
        raise HTTPException(status_code=404, detail="Difficulty not found")

    rank = get_rank_from_accuracy(score_data.accuracy)

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
    }

