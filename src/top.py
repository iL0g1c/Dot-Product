from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import Int64
from datetime import datetime, timedelta, date

load_dotenv()
DATABASE_TOKEN = os.getenv("DATABASE_TOKEN")
connection_string = f"mongodb://mongo_db_admin:{DATABASE_TOKEN}@45.76.164.130:27017/?directConnection=true&serverSelectionTimeoutMS=2000&authSource=admin&appName=mongosh+1.5.0"
client = MongoClient(connection_string)

def getLeaderboard(server_id, mode, time_span):
    day_date = date.today()
    if time_span == "day":
        period = datetime(day_date.year, day_date.month, day_date.day)
    elif time_span == "week":
        week_date = day_date - timedelta(days=((day_date.isoweekday() + 1) % 7)) + timedelta(days=1)
        period = datetime(week_date.year, week_date.month, week_date.day, 0, 0, 0)
    elif time_span == "month":
        period = datetime(day_date.year, day_date.month, 1)
    elif time_span == "all":
        period = datetime(1000, day_date.month, 1)
        
    db = client["dotproduct"]
    if mode == "flights":
        patrolCollection = db["patrols"]
        events = list(patrolCollection.find({
            "$and": [
                {"$and": [
                    {"end": {"$gte": period}},
                    {"type": {"$eq": "flight"}}
                ]},
                {"server_id": Int64(server_id)}
            ]
        }))
    elif mode == "radars":
        patrolCollection = db["patrols"]
        events = list(patrolCollection.find({
            "$and": [
                {"$and": [
                    {"end": {"$gte": period}},
                    {"type": {"$eq": "radar"}}
                ]},
                {"server_id": Int64(server_id)}
            ]
        }))
    elif mode == "kills":
        killCollection = db["kills"]
        events = list(killCollection.find({
            "$and": [
                {"end": {"$gte": period}},
                {"server_id": Int64(server_id)}
            ]
        }))
    elif mode == "disables":
        disableCollection = db["disables"]
        events = list(disableCollection.find({
            "$and": [
                {"end": {"$gte": period}},
                {"server_id": Int64(server_id)}
            ]
        }))
    elif mode == "sars":
        sarCollection = db["sars"]
        events = list(sarCollection.find({
            "$and": [
                {"end": {"$gte": period}},
                {"server_id": Int64(server_id)}
            ]
        }))
        

    #tally up event counts
    user_counts = {}
    for event in events:
        user_id = event["user_id"]
        if user_id in user_counts:
            user_counts[user_id] += 1
        else:
            user_counts[user_id] = 1
    event_tallies = [{'user_id': user_id, 'counts': count} for user_id, count in user_counts.items()]

    #rank users
    processed_data = sorted(event_tallies, key=lambda x: x['counts'], reverse=True)

    return processed_data