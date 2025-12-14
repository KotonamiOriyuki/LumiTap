# Created: Dec 14, 19:00
# Version 1.0
# beatmaps management

from fastapi import APIRouter, Depends, UploadFile, File, Form
from backend.app.database import beatmaps_collection, difficulties_collection
from backend.app.utils.security import get_current_user
import uuid
import json

router = APIRouter()

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

    # TODO: 暂定这里是用json储存，用note和time分析物件时间
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