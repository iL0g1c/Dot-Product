from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import Int64
import jsonlines
from datetime import datetime


def string2Datetime(input_string):
    if input_string:
        input_format = "%Y-%m-%d %H:%M:%S.%f"

        dt_object = datetime.strptime(input_string, input_format)
        rounded_dt = dt_object.replace(microsecond=0)
        return rounded_dt
    return None

def loadJson(file):
    data = []
    with jsonlines.open(file) as reader:
       for item in reader:
           data.append(item)
    reader.close()
    return data

def convert():
    print("Connecting to database...")
    load_dotenv()
    DATABASE_TOKEN = os.getenv("DATABASE_TOKEN")
    connection_string = f"mongodb://mongo_db_admin:{DATABASE_TOKEN}@45.76.164.130:27017/?directConnection=true&serverSelectionTimeoutMS=2000&authSource=admin&appName=mongosh+1.5.0"
    client = MongoClient(connection_string)

    print("Uploading global Data...")
    client.drop_database("dotproduct")
    db = client["dotproduct"]
    globalCollection = db["global_data"]
    event_id = loadJson("../legacy_database/data.jl")[0]["ids"]
    globalCollection.insert_one({"ids": event_id})
    

    guilds = loadJson("../legacy_database/guilds.jl")
    for guild in guilds:
        userCollection = db["users"]
        patrolCollection = db["patrols"]
        killCollection = db["kills"]
        disableCollection = db["disables"]
        sarCollection = db["sars"]
        guild_data = loadJson(f"../legacy_database/{guild['file']}")
        for item in guild_data:
            print(f"item {guild_data.index(item)} of guild {guild['id']}")
            if item["sar_needed"] == "yes":
                sar_needed = True
            else:
                sar_needed = False
            userCollection.insert_one({
                "user_id": Int64(item["user"]),
                "server_id": Int64(guild["id"]),
                "sar_needed": sar_needed
            })

            for patrol in item["patrols"]:
                patrolCollection.insert_one({
                    "id": Int64(patrol["id"]),
                    "type": "flight",
                    "user_id": Int64(item["user"]),
                    "server_id": Int64(guild["id"]),
                    "start": string2Datetime(patrol["start"]),
                    "end": string2Datetime(patrol["end"])
                })

            for patrol in item["radars"]:
                patrolCollection.insert_one({
                    "id": Int64(patrol["id"]),
                    "type": "radar",
                    "user_id": Int64(item["user"]),
                    "server_id": Int64(guild["id"]),
                    "start": string2Datetime(patrol["start"]),
                    "end": string2Datetime(patrol["end"])
                })

            for kill in item["kills"]:
                killCollection.insert_one({
                    "id": Int64(kill["id"]),
                    "end": string2Datetime(kill["end"]),
                    "user_id": Int64(item["user"]),
                    "server_id": Int64(guild["id"])
                })

            for disable in item["disables"]:
                disableCollection.insert_one({
                    "id": Int64(disable["id"]),
                    "end": string2Datetime(disable["end"]),
                    "user_id": Int64(item["user"]),
                    "server_id": Int64(guild["id"])
                })

            for sar in item["sars"]:
                sarCollection.insert_one({
                    "id": Int64(sar["id"]),
                    "end": string2Datetime(sar["end"]),
                    "user_id": Int64(item["user"]),
                    "server_id": Int64(guild["id"]),
                    "pilot_id": sar["pilot"]
                })

convert()