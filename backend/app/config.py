# Created: Dec 13 18:00
# Version 1.0
# Connection between backends and the database
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "lumitap"
    SECRET_KEY: str = "lumitap-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 30

settings = Settings()