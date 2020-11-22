from pymongo import MongoClient
def mongoconnect():
    db=MongoClient().mydb
    return db
