from flask import Flask, render_template, request
app = Flask(__name__)

from pymongo import MongoClient
from bson.objectid import ObjectId

import os
import json
import re

regexp = r'(([\d同一二三四五六七八九十]+年[、同某\d一二三四五六七八九十零]*月[初間某\d卅廿一二三四五六七八九十零]+日?).+?)+(?<=竊.)(.{1,30})'

MONGODB_URI = os.environ['MONGODB_URI']
client = MongoClient(MONGODB_URI)
db = client.wenizit
judgements = db.judgements

@app.route('/')
def index():
    return render_template('index.html',
                            judgements=list(judgements.find()))

@app.route('/<jid>')
def judgement(jid=None):
    j = judgements.find_one({'_id': ObjectId(jid)})
    raw = j['content']
    split = re.split(regexp, raw)
    content = []
    count_of_date = 0
    for text in split:
        if re.match(regexp, text) is not None:
            count_of_date += 1
            if text == date:
                content.append({'text': text, 'is_date': True, 'select': True})
            else:
                content.append({'text': text, 'is_date': True, 'select': False})
        else:
            content.append({'text': text, 'is_date': False, 'select': False})

    return render_template('judgement.html',
                            content=content,
                            judgement=j,
                            count_of_date=count_of_date)

@app.route('/<jid>/save', methods=['POST'])
def save(jid=None):
    try:
        j = judgements.find_one({'_id': ObjectId(jid)})
        dates = request.form.getlist('chosen-date')
        judgements.update_one({'_id': ObjectId(jid)},
                              {'$set': {'dates': dates}},
                              upsert=False)
        return 'Ok! <a href="/{jid}">Go back</a> to the list.'
    except:
        return 'Something went wrong. <a href="/{jid}">Go back</a> and try again.'.format(jid=jid)
