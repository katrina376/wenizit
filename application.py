from flask import Flask, render_template, request
app = Flask(__name__)

from pymongo import MongoClient
from bson.objectid import ObjectId

import os
import json
import re

# SETTINGS
regexp = r'([\d同一二三四五六七八九十]+年[、同某\d一二三四五六七八九十零]*月[初間某\d卅廿一二三四五六七八九十零]+日?)'
keywords = [
    {'text':'竊', 'prev': 30, 'color': 'light'},
    {'text':'引用', 'prev': 0, 'color': 'important'}
]

uri = os.environ['MONGODB_URI']
client = MongoClient(uri,
                     connectTimeoutMS=30000,
                     socketTimeoutMS=None,
                     socketKeepAlive=True)
db = client.get_default_database()
judgements = db.judgements

@app.route('/')
def index():
    pagination_len = 40
    per_page = 80

    page_num = int(request.args.get('p', 1))

    show = request.args.get('show', 'false')
    if show == 'false':
        query = judgements.find({'state': False}).sort('_id')
        q = ''
    elif show == 'true':
        query = judgements.find({'state': True}).sort('_id')
        q = '&show=true'
    else:
        query = judgements.find().sort('_id')
        q = '&show=both'

    part = query.skip((page_num - 1) * per_page).limit(per_page)
    all_page_num = int(query.count() / per_page) + 1

    if all_page_num < pagination_len:
        lb = 1
        ub = all_page_num
    elif page_num < pagination_len:
        lb = 1
        ub = min(all_page_num, pagination_len)
    elif page_num > all_page_num - pagination_len:
        lb = all_page_num - pagination_len
        ub = all_page_num
    else:
        lb = page_num - int(pagination_len / 2)
        ub = page_num + int(pagination_len / 2)
    return render_template('index.html',
                            judgements=list(part),
                            per_page=per_page,
                            current_page_num=page_num,
                            all_page_num=all_page_num,
                            lb=lb,
                            ub=ub,
                            q=q)

# TODO: comment
@app.route('/j/<jid>')
def judgement(jid=None):
    j = judgements.find_one({'_id': ObjectId(jid)})
    raw = j['事實理由']
    process = list(({'idx': idx, 'char': char, 'highlight': False, 'color': ''} for idx, char in enumerate(raw)))

    # Search for highlight
    for keyword in keywords:
        highlights = re.finditer(re.compile(keyword['text']), raw)
        print(highlights)
        for m in highlights:
            start = max(m.start() - keyword['prev'], 0)
            end = m.end()
            for d in process[start:end]:
                d['highlight'] = True
                d['color'] = keyword['color']

    split = re.split(regexp, raw)
    content = []
    count_of_date = 0
    for text in split:
        start = raw.index(text)
        end = start + len(text)
        if re.match(regexp, text) is not None:
            count_of_date += 1
            if text in j['dates']:
                content.append({
                    'text': ''.join([p['char'] for p in process[start:end]]),
                    'chars': list(process[start:end]),
                    'is_date': True,
                    'select': True
                })
            else:
                content.append({
                    'text': ''.join([p['char'] for p in process[start:end]]),
                    'chars': list(process[start:end]),
                    'is_date': True,
                    'select': False
                })
        else:
            content.append({
                'text': ''.join([p['char'] for p in process[start:end]]),
                'chars': list(process[start:end]),
                'is_date': False,
                'select': False
            })

    return render_template('judgement.html',
                            content=content,
                            judgement=j,
                            count_of_date=count_of_date)

@app.route('/j/<jid>/save', methods=['POST'])
def save(jid=None):
    try:
        j = judgements.find({'_id': ObjectId(jid)}).sort("_id").limit(1)
        dates = request.form.getlist('chosen-date')
        judgements.update_one({'_id': ObjectId(jid)},
                              {'$set': {'dates': dates, 'state': True}},
                              upsert=False)
        n = judgements.find({'_id': {'$gt': ObjectId(jid) },
                             'state': False}).sort('_id').limit(1)
        if n.count() > 0:
            return 'Successfully saved! Go to <a href="/j/{jid}">the next document</a>.'.format(jid=n[0]['_id'])
        else:
            return 'Successfully saved! Go back to <a href="/?show=both">the list</a>.'
    except:
        return 'Something went wrong. <a href="/j/{jid}">Go back</a> and try again.'.format(jid=jid)

@app.route('/j/<jid>/pass')
def pass_over(jid=None):
    try:
        j = judgements.find_one({'_id': ObjectId(jid)})
        judgements.update_one({'_id': ObjectId(jid)},
                              {'$set': {'dates': [], 'state': True}},
                              upsert=False)
        n = judgements.find({'_id': {'$gt': ObjectId(jid) },
                             'state': False}).sort('_id').limit(1)
        if n.count() > 0:
            return 'Successfully saved! Go to <a href="/j/{jid}">the next document</a>.'.format(jid=n[0]['_id'])
        else:
            return 'Successfully saved! Go back to <a href="/?show=both">the list</a>.'
    except:
        return 'Something went wrong. <a href="/j/{jid}">Go back</a> and try again.'.format(jid=jid)

@app.route('/j/<jid>/skip')
def skip(jid=None):
    try:
        j = judgements.find_one({'_id': ObjectId(jid)})
        judgements.update_one({'_id': ObjectId(jid)},
                              {'$set': {'tag': True}},
                              upsert=False)
        n = judgements.find({'_id': {'$gt': ObjectId(jid) },
                             'state': False}).sort('_id').limit(1)
        if n.count() > 0:
            return 'Temporarily skipped! Go to <a href="/j/{jid}">the next document</a>.'.format(jid=n[0]['_id'])
        else:
            return 'Temporarily skipped! Go back to <a href="/?show=both">the list</a>.'
    except:
        return 'Something went wrong. <a href="/j/{jid}">Go back</a> and try again.'.format(jid=jid)
