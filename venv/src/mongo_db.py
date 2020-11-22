import pymongo
import pandas as pd


class Mongo_db:
    def __init__(self):
        # connecting to mongodb and getting the database and collection
        self.mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mydb = self.mongoClient["bda-project"]  # database name
        self.mycol = self.mydb["googleplaystore"]  # collection name

    def insertDocument(self, doc):
        try:
            res = self.mycol.insert_one(doc)
            return res.inserted_id
        except Exception:
            return None

    def updateDocument(self, query, newVal, multiple=False):
        try:
            newValues = {"$set": newVal}
            res = self.mycol.update_one(
                query, newValues) if not multiple else self.mycol.update_many(query, newValues)
            return res.modified_count
        except Exception:
            return None

    def deleteDocument(self, query, multiple=False):
        try:
            res = self.mycol.delete_one(query) if not multiple else self.mycol.delete_many(query)
            return res.deleted_count
        except Exception:
            return None

    def searchData(self, query, projection, sortField="", sortOrder=0):
        # returns pandas dataframe of the result
        try:
            if sortField == "" or sortOrder == 0:
                res = self.mycol.find(query, projection)
                return pd.DataFrame(list(res))
            else:
                res = self.mycol.find(query, projection).sort(
                    sortField, sortOrder)
                return pd.DataFrame(list(res))
        except Exception:
            return None

    def deleteCollection(self):
        try:
            self.mycol.drop()
            return True
        except Exception:
            return False
