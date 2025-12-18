# Created: Dec 13 18:10
# Version 1.1
# Changelog: Dec 14 20:05 -> changed the import of settings
# Structure and abbv. of each database collections

from pymongo import MongoClient
from backend.app.config import settings

client = MongoClient(settings.MONGODB_URL)
db = client[settings.DATABASE_NAME]

users_collection = db["users"]
beatmaps_collection = db["beatmaps"]
difficulties_collection = db["difficulties"]
scores_collection = db["scores"]
forum_sections_collection = db["forum_sections"]
forum_posts_collection = db["forum_posts"]

users_collection.create_index("username", unique=True)
users_collection.create_index("uid", unique=True)
beatmaps_collection.create_index("sid", unique=True)
difficulties_collection.create_index("bid", unique=True)
scores_collection.create_index("scid", unique=True)
forum_posts_collection.create_index("fid", unique=True)