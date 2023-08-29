from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_TOKEN = os.getenv("DATABASE_TOKEN")
connection_string = f"mongodb://mongo_db_admin:{DATABASE_TOKEN}@45.76.164.130:27017/?directConnection=true&serverSelectionTimeoutMS=2000&authSource=admin&appName=mongosh+1.5.0"
client = MongoClient(connection_string)

client["dotproduct"]["global_data"].insert_one({
    "_id": 1,
    "ids": 0
})