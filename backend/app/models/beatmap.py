# Created Dec 14
# Version 1.0
# models of beatmap management

from pydantic import BaseModel
from typing import List, Optional

class DifficultyCreate(BaseModel):
    name: str
    level: float
    chart_data: dict

class BeatmapCreate(BaseModel):
    title: str
    artist: str
    bpm: int

class DifficultyResponse(BaseModel):
    bid: str
    name: str
    level: float
    note_count: int

class BeatmapResponse(BaseModel):
    sid: str
    title: str
    artist: str
    bpm: int
    background: Optional[str] = None
    audio: Optional[str] = None
    uploader_uid: str
    uploader_name: str
    difficulties: List[DifficultyResponse]