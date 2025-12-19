# Created: Dec 19, 16:00
# Ver 1.0
# API Calling functions of forum view
import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from ..database import db
from ..utils.security import get_current_user

router = APIRouter(prefix="/api/forum", tags=["forum"])


class ThreadCreate(BaseModel):
    title: str
    content: str


class ReplyCreate(BaseModel):
    content: str


def safe_oid(id_str: str):
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        return None


def get_user_by_id(uid: str):
    if not uid:
        return None
    oid = safe_oid(uid)
    if oid:
        user = db.users.find_one({"_id": oid})
        if user:
            return user
    return db.users.find_one({"uid": uid})

# Jiarui Li: fetch all forum sections to display
@router.get("/sections")
def get_sections():
    sections = list(db.forum_sections.find().sort("order", 1))
    result = []

    for sec in sections:
        sec_id = str(sec["_id"])
        subs = list(db.forum_subforums.find({"section_id": sec_id}))
        sub_list = []

        for sf in subs:
            sf_id = str(sf["_id"])
            tc = db.forum_threads.count_documents({"subforum_id": sf_id})
            pc = db.forum_posts.count_documents({"subforum_id": sf_id})
            sub_list.append({
                "id": sf_id,
                "_id": sf_id,
                "name": sf.get("name", ""),
                "description": sf.get("description", ""),
                "thread_count": tc,
                "post_count": pc
            })

        result.append({
            "id": sec_id,
            "name": sec.get("name", ""),
            "description": sec.get("description", ""),
            "subforums": sub_list
        })

    return result

# Jiarui Li: Return all threads in the subforum
@router.get("/subforum/{sfid}")
def get_subforum(sfid: str):
    oid = safe_oid(sfid)
    if not oid:
        raise HTTPException(400, "Invalid ID")
    sf = db.forum_subforums.find_one({"_id": oid})
    if not sf:
        raise HTTPException(404, "Not found")
    return {
        "id": str(sf["_id"]),
        "name": sf.get("name", ""),
        "description": sf.get("description", "")
    }

# Zheng Wu: get the specific thread post/replies statistics
@router.get("/subforum/{sfid}/threads")
def get_threads(sfid: str):
    oid = safe_oid(sfid)
    if not oid:
        raise HTTPException(400, "Invalid ID")
    sf = db.forum_subforums.find_one({"_id": oid})
    if not sf:
        raise HTTPException(404, "Not found")

    threads = list(db.forum_threads.find({"subforum_id": sfid}).sort("created_at", -1).limit(50))
    result = []

    for t in threads:
        author = get_user_by_id(t.get("author_id"))
        rc = db.forum_posts.count_documents({"thread_id": str(t["_id"]), "is_first": {"$ne": True}})
        ca = t.get("created_at")
        if isinstance(ca, datetime):
            ca = ca.timestamp()
        result.append({
            "id": str(t["_id"]),
            "title": t.get("title", ""),
            "author_name": author.get("username", "Unknown") if author else "Unknown",
            "author_id": t.get("author_id"),
            "author_avatar": author.get("avatar") if author else None,
            "created_at": ca or 0,
            "reply_count": rc
        })

    return {
        "subforum": {
            "id": str(sf["_id"]),
            "name": sf.get("name", ""),
            "description": sf.get("description", "")
        },
        "threads": result
    }

# Zheng Wu: forum post
@router.post("/subforum/{sfid}/threads")
def create_thread(sfid: str, data: ThreadCreate, user: dict = Depends(get_current_user)):
    oid = safe_oid(sfid)
    if not oid:
        raise HTTPException(400, "Invalid ID")
    sf = db.forum_subforums.find_one({"_id": oid})
    if not sf:
        raise HTTPException(404, "Not found")

    now = datetime.utcnow()
    doc = {
        "subforum_id": sfid,
        "author_id": user["uid"],
        "title": data.title,
        "content": data.content,
        "created_at": now,
        "updated_at": now
    }
    res = db.forum_threads.insert_one(doc)
    tid = str(res.inserted_id)

    post = {
        "thread_id": tid,
        "subforum_id": sfid,
        "author_id": user["uid"],
        "content": data.content,
        "created_at": now,
        "is_first": True,
        "fid": str(uuid.uuid4())
    }
    db.forum_posts.insert_one(post)

    return {"id": tid}

# Jiarui Li: fetch all posts/replies in the thread
@router.get("/thread/{tid}")
def get_thread(tid: str):
    oid = safe_oid(tid)
    if not oid:
        raise HTTPException(400, "Invalid ID")
    t = db.forum_threads.find_one({"_id": oid})
    if not t:
        raise HTTPException(404, "Not found")

    author = get_user_by_id(t.get("author_id"))
    ca = t.get("created_at")
    if isinstance(ca, datetime):
        ca = ca.timestamp()

    thread_info = {
        "id": str(t["_id"]),
        "subforum_id": t.get("subforum_id", ""),
        "title": t.get("title", ""),
        "content": t.get("content", ""),
        "author_name": author.get("username", "Unknown") if author else "Unknown",
        "author_avatar": author.get("avatar") if author else None,
        "author_id": t.get("author_id"),
        "created_at": ca or 0
    }

    posts = list(db.forum_posts.find({"thread_id": tid, "is_first": {"$ne": True}}).sort("created_at", 1).limit(100))
    post_list = []

    for p in posts:
        pa = get_user_by_id(p.get("author_id"))
        pca = p.get("created_at")
        if isinstance(pca, datetime):
            pca = pca.timestamp()
        post_list.append({
            "id": str(p["_id"]),
            "content": p.get("content", ""),
            "author_name": pa.get("username", "Unknown") if pa else "Unknown",
            "author_avatar": pa.get("avatar") if pa else None,
            "author_id": p.get("author_id"),
            "created_at": pca or 0
        })

    return {"thread": thread_info, "posts": post_list}


# Jiarui Li: reply a forum
@router.post("/thread/{tid}/reply")
def reply_thread(tid: str, data: ReplyCreate, user: dict = Depends(get_current_user)):
    oid = safe_oid(tid)
    if not oid:
        raise HTTPException(400, "Invalid ID")
    t = db.forum_threads.find_one({"_id": oid})
    if not t:
        raise HTTPException(404, "Not found")

    now = datetime.now()
    post = {
        "thread_id": tid,
        "subforum_id": t.get("subforum_id", ""),
        "author_id": user["uid"],
        "content": data.content,
        "created_at": now,
        "is_first": False,
        "fid": str(uuid.uuid4())
    }
    res = db.forum_posts.insert_one(post)
    db.forum_threads.update_one({"_id": oid}, {"$set": {"updated_at": now}})

    return {"id": str(res.inserted_id)}

# Zheng Wu: this is debug only to initialize an empty database
@router.post("/init")
def init_forum():
    if db.forum_sections.find_one():
        return {"message": "Already initialized"}

    sections = [
        {"name": "General", "description": "General discussion", "order": 1},
        {"name": "Beatmaps", "description": "Beatmap discussion", "order": 2},
        {"name": "Help", "description": "Help and support", "order": 3}
    ]

    subs = {
        "General": [
            {"name": "Announcements", "description": "Official announcements"},
            {"name": "Introductions", "description": "Introduce yourself"},
            {"name": "Off-Topic", "description": "Random discussions"}
        ],
        "Beatmaps": [
            {"name": "Beatmap Discussion", "description": "Discuss beatmaps"},
            {"name": "Beatmap Requests", "description": "Request beatmaps"},
            {"name": "WIP Beatmaps", "description": "Work in progress"}
        ],
        "Help": [
            {"name": "Technical Support", "description": "Technical issues"},
            {"name": "Gameplay Help", "description": "Gameplay questions"},
            {"name": "Bug Reports", "description": "Report bugs"}
        ]
    }

    for sec in sections:
        res = db.forum_sections.insert_one(sec)
        sid = str(res.inserted_id)
        for sf in subs.get(sec["name"], []):
            sf["section_id"] = sid
            db.forum_subforums.insert_one(sf)

    return {"message": "Forum initialized"}