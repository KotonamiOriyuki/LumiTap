# Created: Dec 15, 19:30
# Ver 1.0
# Basic models related to score submitting and fetching
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ScoreCreate(BaseModel):
    bid: str
    score: int
    accuracy: float
    great_count: int
    good_count: int
    miss_count: int
    max_combo: int

class ScoreResponse(BaseModel):
    scid: str
    uid: str
    username: str
    bid: str
    score: int
    accuracy: float
    rank: str
    great_count: int
    good_count: int
    miss_count: int
    max_combo: int
    potential: float
    created_at: datetime