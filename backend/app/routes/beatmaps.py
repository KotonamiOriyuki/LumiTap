# Created: Dec 14, 19:00
# Version 1.2
# beatmaps management
# Modified: Dec 14, 21:00 -> added searching algorithm
# Dec 15, 19:00 -> Remove the TODO comment for beatmap structure

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from backend.app.database import beatmaps_collection, difficulties_collection, users_collection
from backend.app.utils.security import get_current_user
import uuid
import json

router = APIRouter()

# Zixiao Shen: Use LCS to match the song title

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

#  Chenxi Liu: obtain the whole beatmap set of a song
# BeatmapSetId(sid) > BeatmapId(bid)
@router.get("/api/beatmaps/{sid}")
def get_beatmap(sid: str):
    beatmap = beatmaps_collection.find_one({"sid": sid})
    if not beatmap:
        raise HTTPException(status_code=404, detail="Beatmap not found")

    diffs = list(difficulties_collection.find({"sid": sid}).sort("level", 1))
    uploader = users_collection.find_one({"uid": beatmap["uploader_uid"]})

    return {
        "sid": beatmap["sid"],
        "title": beatmap["title"],
        "artist": beatmap["artist"],
        "bpm": beatmap["bpm"],
        "background": beatmap.get("background"),
        "audio": beatmap.get("audio"),
        "uploader_uid": beatmap["uploader_uid"],
        "uploader_name": uploader["username"] if uploader else "Unknown",
        "difficulties": [
            {"bid": d["bid"], "name": d["name"], "level": d["level"], "note_count": d.get("note_count", 0)}
            for d in diffs
        ]
    }


# Chenxi Liu: Obtain the difficulty of a specific beatmap id
@router.get("/api/beatmaps/difficulty/{bid}")
def get_difficulty(bid: str):
    diff = difficulties_collection.find_one({"bid": bid})
    if not diff:
        raise HTTPException(status_code=404, detail="Difficulty not found")

    beatmap = beatmaps_collection.find_one({"sid": diff["sid"]})
    return {
        "bid": diff["bid"],
        "sid": diff["sid"],
        "name": diff["name"],
        "level": diff["level"],
        "chart_data": diff["chart_data"],
        "note_count": diff.get("note_count", 0),
        "beatmap": {
            "title": beatmap["title"],
            "artist": beatmap["artist"],
            "bpm": beatmap["bpm"],
            "background": beatmap.get("background"),
            "audio": beatmap.get("audio")
        } if beatmap else None
    }

# Chenxi Liu: Upload Management
@router.post("/api/beatmaps/upload")
async def upload_beatmap(
        title: str = Form(...),
        artist: str = Form(...),
        bpm: int = Form(...),
        background: UploadFile = File(...),
        audio: UploadFile = File(...),
        difficulties: str = Form(...),
        current_user: dict = Depends(get_current_user)
):
    sid = str(uuid.uuid4())[:8]
    while beatmaps_collection.find_one({"sid": sid}):
        sid = str(uuid.uuid4())[:8]

    bg_ext = background.filename.split(".")[-1]
    bg_filename = f"{sid}_bg.{bg_ext}"
    bg_path = f"app/uploads/backgrounds/{bg_filename}"
    with open(bg_path, "wb") as f:
        f.write(await background.read())

    audio_ext = audio.filename.split(".")[-1]
    audio_filename = f"{sid}_audio.{audio_ext}"
    audio_path = f"app/uploads/audio/{audio_filename}"
    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    beatmap_doc = {
        "sid": sid,
        "title": title,
        "artist": artist,
        "bpm": bpm,
        "background": f"/uploads/backgrounds/{bg_filename}",
        "audio": f"/uploads/audio/{audio_filename}",
        "uploader_uid": current_user["uid"]
    }
    beatmaps_collection.insert_one(beatmap_doc)

    diffs_data = json.loads(difficulties)
    for d in diffs_data:
        bid = str(uuid.uuid4())[:8]
        while difficulties_collection.find_one({"bid": bid}):
            bid = str(uuid.uuid4())[:8]

        chart = d["chart_data"]
        note_count = len(chart.get("notes", []))

        diff_doc = {
            "bid": bid,
            "sid": sid,
            "name": d["name"],
            "level": d["level"],
            "chart_data": chart,
            "note_count": note_count
        }
        difficulties_collection.insert_one(diff_doc)

    return {"sid": sid, "message": "Beatmap uploaded successfully"}