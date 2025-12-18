# Created: Dec 12, 15:30
# Ver 1.2
# Changelog:
# Dec 14, 20:00 -> 1.1 Added beatmaps management router
# Dec 15, 21:00 -> 1.2 Added score and session management router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .routes import auth, beatmaps, scores, users

app = FastAPI(title="LumiTap API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uploads_path = os.path.join(os.path.dirname(__file__), "uploads")
if os.path.exists(uploads_path):
    app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")

# Yiwen Wang: Required for further developments
app.include_router(auth.router)
app.include_router(beatmaps.router)
app.include_router(scores.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "LumiTap API is running"}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}