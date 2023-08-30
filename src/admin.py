from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import Int64, ObjectId

load_dotenv()
DATABASE_TOKEN = os.getenv("DATABASE_TOKEN")
connection_string = f"mongodb://mongo_db_admin:{DATABASE_TOKEN}@45.76.164.130:27017/?directConnection=true&serverSelectionTimeoutMS=2000&authSource=admin&appName=mongosh+1.5.0"
client = MongoClient(connection_string)

def makeSuperuser(user_id, server_id, action):
    db = client["dotproduct"]
    userCollection = db["users"]
    user = list(userCollection.find({
        "$and": [
            {"user_id": {"$eq": Int64(user_id)}},
            {"server_id": {"$eq": Int64(server_id)}}
        ]
    }))

    if user == []:
        # User not in database.
        return 1

    if action == 1:
        if user[0]["superuser"]:
            # Already a super user.
            return 2
        userCollection.update_one(
            {"user_id": Int64(user_id)},
            {"$set": {"superuser": True}}
        )
    elif action == 2:
        if not user[0]["superuser"]:
            return 3
        userCollection.update_one(
            {"user_id": Int64(user_id)},
            {"$set": {"superuser": False}}
        )
    return None

# add removal