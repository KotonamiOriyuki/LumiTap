# Created: Dec 19, 15:00
# Ver 1.0
# Basic models related to forum/subforum post/response

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ForumPostCreate(BaseModel):
    section_id: str
    title: str
    content: str

class SubforumSection(BaseModel):
    id: str
    name: str
    description: str
    latest_topic: Optional[str] = None
    latest_poster_uid: Optional[str] = None
    latest_poster_name: Optional[str] = None
    latest_time: Optional[datetime] = None

class ForumSectionResponse(BaseModel):
    title: str
    subforums: List[SubforumSection]