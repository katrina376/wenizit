from pymongo import MongoClient
import os
import json

MONGODB_URI = os.environ['MONGODB_URI']
client = MongoClient(MONGODB_URI)
db = client.wenizit
db.judgements.drop()
judgements = db.judgements

with open('data/data.json', 'r') as f:
    string = f.read()
    judgement = json.loads(string)
    for j in judgement:
        j['dates'] = []
        judgements.insert_one(j)
