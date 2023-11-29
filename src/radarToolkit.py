from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import Int64
from geofs import MapAPI

class RadarToolkit():
    def __init__(self):
        load_dotenv()
        DATABASE_TOKEN = os.getenv("DATABASE_TOKEN")
        connection_string = f"mongodb://mongo_db_admin:{DATABASE_TOKEN}@45.76.164.130:27017/?directConnection=true&serverSelectionTimeoutMS=2000&authSource=admin&appName=mongosh+1.5.0"
        self.client = MongoClient(connection_string)

    def getRadarActiveGuilds(self):
        db = self.client["dotproduct"]
        guildCollection = db["guilds"]
        radarActiveGuilds = []
        guilds = guildCollection.find({"radarEnabled": True})
        for guild in guilds:
            radarActiveGuilds.append({
                "guild_id": guild["server_id"],
                "radarLogChannel": guild["radarLogChannel"]
            })
        return guilds


            
    
    def fetchGeoFSUsers(self):
        api = MapAPI()
        data = api.getUsers(foos=False)
        callsigns = []
        for pilot in data:
            callsigns.append({
                "callsign": pilot.userInfo["callsign"],
                "aircraft": pilot.aircraft,
                "coordinates": pilot.coordinates
            })
        return callsigns

    def radarEnabled(self, server_id):
        db = self.client["dotproduct"]
        guildCollection = db["guilds"]

        guild = list(guildCollection.find({"id": server_id}))
        if not guild:
            return None, 9
        else:
            if guild[0]["radarEnabled"] == True:
                return True
            elif guild[0]["radarEnabled"] == False:
                return False
            else:
                return None
    def setRadar(self, mode, server_id):
        db = self.client["dotproduct"]
        guildCollection = db["guilds"]
        if mode:
            guildCollection.update_one(
                {"id": {"$eq": Int64(server_id)}},
                {"$set": {"radarEnabled": True}}
            )
        else:
            guildCollection.update_one(
                {"id": {"$eq": Int64(server_id)}},
                {"$set": {"radarEnabled": False}}
            )
        guilds = guildCollection.find({"id": server_id}, {"radarLogChannel": 1})
        for guild in guilds:
            return guild["radarLogChannel"]