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
        print(user_id, server_id)
        userCollection.update_one(
            {"$and": [
                {"user_id": {"$eq": Int64(user_id)}},
                {"server_id": {"$eq": Int64(server_id)}}
            ]},
            {"$set": {"superuser": True}}
        )
    elif action == 2:
        if not user[0]["superuser"]:
            return 3
        userCollection.update_one(
            {"$and": [
                {"user_id": {"$eq": Int64(user_id)}},
                {"server_id": {"$eq": Int64(server_id)}}
            ]},
            {"$set": {"superuser": False}}
        )
    return None

def removeEvent(user_id, server_id, event_id):
    db = client["dotproduct"]

    user = list(db["users"].find({
        "$and": [
            {"user_id": user_id},
            {"server_id": server_id}
        ]
    }))

    if not user:
        return 1
    else:
        if not user[0]["superuser"]:
            return 6


    data = list(db["patrols"].find({
        "$and": [
            {"server_id": server_id},
            {"id": event_id}
         ]
    }))
    if data:
        db["patrols"].delete_one({"id": event_id})
        return None

    data = list(db["kills"].find({
        "$and": [
            {"server_id": server_id},
            {"id": event_id}
         ]
    }))
    if data:
        db["kills"].delete_one({"id": event_id})
        return None

    data = list(db["disables"].find({
        "$and": [
            {"server_id": server_id},
            {"id": event_id}
         ]
    }))
    if data:
        db["disables"].delete_one({"id": event_id})
        return None

    data = list(db["sars"].find({
        "$and": [
            {"server_id": server_id},
            {"id": event_id}
         ]
    }))
    if data:
        db["sars"].delete_one({"id": event_id})
        return None
    
    return 7

def savePatrolChannel(channel_id, server_id):
    db = client["dotproduct"]
    guildCollection = db["guilds"]

    # check if guild is registered
    guild = list(guildCollection.find({"id": server_id}))
    if not guild:
        # create guild document
        guildCollection.insert_one({
            "id": Int64(server_id),
            "logChannel": channel_id
        })
    else:
        # update guild document
        guildCollection.update_one(
            {"id": {"$eq": Int64(server_id)}},
            {"$set": {"logChannel": channel_id}}
        )

def getLogChannel(server_id):
    db = client["dotproduct"]
    guildCollection = db["guilds"]
    
    guild = list(guildCollection.find({"id": server_id}))
    if not guild:
        return None, 8
    else:
        return guild[0]["logChannel"], None