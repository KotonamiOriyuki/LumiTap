# Created: Dec 12, 15:30
# Ver 1.0

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

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
# app.include_router(routers)

@app.get("/")
def root():
    return {"message": "LumiTap API is running"}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}