from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import Int64

load_dotenv()
DATABASE_TOKEN = os.getenv("DATABASE_TOKEN")
connection_string = f"mongodb://mongo_db_admin:{DATABASE_TOKEN}@45.76.164.130:27017/?directConnection=true&serverSelectionTimeoutMS=2000&authSource=admin&appName=mongosh+1.5.0"
client = MongoClient(connection_string)

def kill(user_id, server_id, datetime_amount):
    db = client["dotproduct"]

    globalCollection = db["global_data"]
    globalCollection.update_one({"ids": list(globalCollection.find())[0]["ids"]}, {"$inc": {"ids": 1}})
    event_id = list(globalCollection.find())[0]["ids"]

    killCollection = db["kills"]
    killCollection.insert_one({
        "id": Int64(event_id),
        "end": datetime_amount,
        "user_id": Int64(user_id),
        "server_id": Int64(server_id),
    })

def disable(user_id, server_id, datetime_amount):
    db = client["dotproduct"]

    globalCollection = db["global_data"]
    globalCollection.update_one({"ids": list(globalCollection.find())[0]["ids"]}, {"$inc": {"ids": 1}})
    event_id = list(globalCollection.find())[0]["ids"]

    disableCollection = db["disables"]
    disableCollection.insert_one({
        "id": Int64(event_id),
        "end": datetime_amount,
        "user_id": Int64(user_id),
        "server_id": Int64(server_id),
    })