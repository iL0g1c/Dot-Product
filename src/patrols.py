from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import Int64, ObjectId
from datetime import timedelta

load_dotenv()
DATABASE_TOKEN = os.getenv("DATABASE_TOKEN")
connection_string = f"mongodb://mongo_db_admin:{DATABASE_TOKEN}@45.76.164.130:27017/?directConnection=true&serverSelectionTimeoutMS=2000&authSource=admin&appName=mongosh+1.5.0"
client = MongoClient(connection_string)

def deleteDuplicatePatrols(user_id, server_id):
    db = client["dotproduct"]
    patrolCollection = db["patrols"]

    patrol = list(patrolCollection.find({
        "$and": [
            {"$and": [
                {"user_id": Int64(user_id)},
                {"server_id": Int64(server_id)}
            ]},
            {"end": {"$type": 10}}
        ]
    }))
    if len(patrol) >= 1:
        for i in range(len(patrol)):
            patrolCollection.delete_many({
                "$and": [
                    {"$and": [
                        {"user_id": Int64(user_id)},
                        {"server_id": Int64(server_id)}
                    ]},
                    {"end": None}
                ]
            })

def getPatrolStats(user_id, server_id):
    patrols = list(client["dotproduct"]["patrols"].find({
        "$and": [
            {"user_id": Int64(user_id)},
            {"server_id": Int64(server_id)}
        ]
    }))

    total = timedelta(seconds=0)
    for i in range(len(patrols)):
        start = patrols[i]["start"]
        end = patrols[i]["end"]
        duration = end - start
        total += duration
    return total, len(patrols)

def patrolOn(user_id, server_id, datetime_amount, patrol_type):
    # Check if user exists.
    # if not create user
    # create start patrol log
    db = client["dotproduct"]
    userCollection = db["users"]
    users = list(userCollection.find({
        "$and": [
            {"user_id": Int64(user_id)},
            {"server_id": Int64(server_id)}
        ]
    })) # check if it adds new users  
    if users == []:
        userCollection.insert_one({
            "user_id": Int64(user_id),
            "server_id": Int64(server_id),
            "sar_needed": False,
            "superuser": False
        })

    patrolCollection = db["patrols"]
    openPatrols = list(patrolCollection.find({
        "$and": [
            {"$and": [
                {"user_id": Int64(user_id)},
                {"server_id": Int64(server_id)}
            ]},
            {"end": {"$type": 10}}
        ]
    }))

    if openPatrols != []:
        return None, 1


    globalCollection = db["global_data"]
    globalCollection.update_one({"ids": list(globalCollection.find())[0]["ids"]}, {"$inc": {"ids": 1}})
    event_id = list(globalCollection.find())[0]["ids"]
    patrolCollection.insert_one({
        "id": Int64(event_id),
        "type": patrol_type,
        "user_id": Int64(user_id),
        "server_id": Int64(server_id),
        "start": datetime_amount,
        "end": None
    })

    return event_id, None

def patrolOff(user_id, server_id, datetime_amount):
    db = client["dotproduct"]
    patrolCollection = db["patrols"]

    patrol = list(patrolCollection.find({
        "$and": [
            {"$and": [
                {"user_id": Int64(user_id)},
                {"server_id": Int64(server_id)}
            ]},
            {"end": {"$type": 10}}
        ]
    }))[0]
    
    patrolCollection.update_one(
        {"id": Int64(patrol["id"])},
        {"$set": {"end": datetime_amount}}
    )

    duration = datetime_amount - patrol["start"]
    start_time = patrol["start"]
    event_id = patrol["id"]
    patrol_type = patrol["type"]


    return duration, start_time, event_id, patrol_type

#stop from creating multiple patrols