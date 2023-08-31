# add log page updater
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import Int64

load_dotenv()
DATABASE_TOKEN = os.getenv("DATABASE_TOKEN")
connection_string = f"mongodb://mongo_db_admin:{DATABASE_TOKEN}@45.76.164.130:27017/?directConnection=true&serverSelectionTimeoutMS=2000&authSource=admin&appName=mongosh+1.5.0"
client = MongoClient(connection_string)

def updatePage(user_id, server_id, mode, items, page):
    # check if user exists
    db = client["dotproduct"]
    userCollection = db["users"]
    user = list(userCollection.find({
        "$and": [
            {"user_id": Int64(user_id)},
            {"server_id": Int64(server_id)}
         ] 
    }))
    if not user:
        return None, None, 1

    # fetch valid data
    match mode:
        # Flight Patrols
        case "flights":
            patrolCollection = db["patrols"]
            data = list(patrolCollection.find({
                "$and": [
                    {"$and": [
                        {"user_id": Int64(user_id)},
                        {"server_id": Int64(server_id)}
                    ]},
                    {"type": "flight"}
                ]
            }))

        # Radar Patrols
        case "radars":
            patrolCollection = db["patrols"]
            data = list(patrolCollection.find({
                "$and": [
                    {"$and": [
                        {"user_id": Int64(user_id)},
                        {"server_id": Int64(server_id)}
                    ]},
                    {"type": "radar"}
                ]
            }))

        # Kills
        case "kills":
            killCollection = db["kills"]
            data = list(killCollection.find({
                "$and": [
                    {"user_id": Int64(user_id)},
                    {"server_id": Int64(server_id)}
                ]
            }))
        # Disables
        case "disables":
            disableCollection = db["disables"]
            data = list(disableCollection.find({
                "$and": [
                    {"user_id": Int64(user_id)},
                    {"server_id": Int64(server_id)}
                ]
            }))

        # sars
        case "sars":
            sarCollection = db["sars"]
            data = list(sarCollection.find({
                "$and": [
                    {"user_id": Int64(user_id)},
                    {"server_id": Int64(server_id)}
                ]
            }))

    # invert list
    data.reverse()
    
    total_items = len(data)
    total_pages = (total_items * items - 1)
    
    start_idx = (page - 1) * items
    end_idx = min(start_idx + items, total_items)

    pruned_data = data[start_idx:end_idx]
    if len(data) <= end_idx:
        edge_alert = True
    else:
        edge_alert = False
    description = ""
    for entry in pruned_data:
        if mode == "flights" or mode == "radars":
            duration = entry["end"] - entry["start"]

            description += f"**ID:** {entry['id']}, **Start Time:** {entry['start']}, **End Time:** {entry['end']}, **Duration:** {duration}\n"
        elif mode == "kills" or mode == "disables":
            description += f"**ID:** {entry['id']}, **Time:** {entry['end']}\n"

        elif mode == "sars":
            description += f"**ID:** {entry['id']}, **Time:** {entry['end']}, **Target:** {entry['pilot_id']}\n"
    return description, edge_alert, None