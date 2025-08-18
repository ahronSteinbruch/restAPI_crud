from pymongo import MongoClient


class DataLoader:
    def __init__(self, mongo_uri: str):
        self.mongo_uri = mongo_uri
        self.connection = None

    def connect(self):
        self.connection = MongoClient(self.mongo_uri)

    def disconnect(self):
        self.connection.close()

    def fetch_all(self,):
        pass
