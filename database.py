import pymongo
from config import MONGO_URI

def connect_db():
    client = pymongo.MongoClient(MONGO_URI)
    db = client["meetup_app_db"]
    return db
