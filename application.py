from functools import wraps

from flask import Flask, render_template, request, Response
app = Flask(__name__)

from pymongo import MongoClient
from bson.objectid import ObjectId

import os
import json
import re

from utils.ara2man import ara2man

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
users = db.users

def check_auth(username, password):
    user = users.find_one({ 'username': username })
    if user is None:
        return False and False
    else:
        return username == user['username'] and password == user['password']

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@requires_auth
def index():
    user = request.authorization.username
    u = users.find({}, {'_id': 0, 'username': 1})[:]
    finish = {}
    finish.update(map(lambda e: (e['username'], judgements.find({'editor': e['username']}).count()), u))

    pagination_len = 40
    per_page = 80

    page_num = int(request.args.get('p', 1))
    query_conds = []

    query_show = ''

    show = request.args.get('show', 'false')
    if show == 'false':
        query_conds.append({'state': False})
        query_show += ''
    elif show == 'true':
        query_conds.append({'state': True})
        query_show += '&show=true'
    else:
        query_conds.append({})
        query_show += '&show=both'

    query_date = ''

    year_ara = request.args.get('syr', '').strip()
    month_ara = request.args.get('smth', '').strip()
    day_ara = request.args.get('sd', '').strip()

    if year_ara != '' and month_ara != '' and day_ara != '':
        year_man = ara2man(year_ara)
        month_man = ara2man(month_ara)
        day_man = ara2man(day_ara)

        query_date += '&syr={year}&smth={month}&sd={day}'.format(year=year_ara, month=month_ara, day=day_ara)

        # Rules of date including abbreviations
        search = [
            re.compile('{year}年{month}月{day}日'.format(year=year_ara, month=month_ara, day=day_ara)),
            re.compile('{year}年{month}月{day}日'.format(year=year_man, month=month_man, day=day_man)),
            re.compile('{year}年.*同年{month}月{day}日'.format(year=year_ara, month=month_ara, day=day_ara)),
            re.compile('{year}年.*同年{month}月{day}日'.format(year=year_man, month=month_man, day=day_man)),
            re.compile('{year}年.*{month}月.*同月{day}日'.format(year=year_ara, month=month_ara, day=day_ara)),
            re.compile('{year}年.*{month}月.*同月{day}日'.format(year=year_man, month=month_man, day=day_man)),
        ]

        query_conds.append({'$or': [{'事實理由': {'$regex': reg}} for reg in search]})

    query = judgements.find({'$and': query_conds})

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
                            search={'year': year_ara, 'month': month_ara, 'day': day_ara},
                            lb=lb,
                            ub=ub,
                            query_show=query_show,
                            query_date=query_date,
                            username=user,
                            finish=finish)

@app.route('/j/<jid>')
@requires_auth
def judgement(jid=None):
    j = judgements.find_one({'_id': ObjectId(jid)})
    raw = j['事實理由']
    process = list(({'idx': idx, 'char': char, 'highlight': False, 'color': ''} for idx, char in enumerate(raw)))

    # Search for highlight
    for keyword in keywords:
        highlights = re.finditer(re.compile(keyword['text']), raw)
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

    count_of_identity = judgements.find({'identity': j['identity']}).count()

    return render_template('judgement.html',
                            content=content,
                            judgement=j,
                            count_of_date=count_of_date,
                            count_of_identity=count_of_identity,
                            )

@app.route('/j/<jid>/save', methods=['POST'])
@requires_auth
def save(jid=None):
    try:
        user = request.authorization.username
        j = judgements.find({'_id': ObjectId(jid)}).sort("_id").limit(1)
        dates = request.form.getlist('chosen-date')
        judgements.update_one({'_id': ObjectId(jid)},
                              {'$set': {'dates': dates, 'state': True, 'editor': user}},
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
@requires_auth
def pass_over(jid=None):
    try:
        user = request.authorization.username
        j = judgements.find_one({'_id': ObjectId(jid)})
        judgements.update_one({'_id': ObjectId(jid)},
                              {'$set': {'dates': [], 'state': True, 'editor': user}},
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
@requires_auth
def skip(jid=None):
    try:
        user = request.authorization.username
        j = judgements.find_one({'_id': ObjectId(jid)})
        judgements.update_one({'_id': ObjectId(jid)},
                              {'$set': {'tag': True, 'editor': user}},
                              upsert=False)
        n = judgements.find({'_id': {'$gt': ObjectId(jid) },
                             'state': False}).sort('_id').limit(1)
        if n.count() > 0:
            return 'Temporarily skipped! Go to <a href="/j/{jid}">the next document</a>.'.format(jid=n[0]['_id'])
        else:
            return 'Temporarily skipped! Go back to <a href="/?show=both">the list</a>.'
    except:
        return 'Something went wrong. <a href="/j/{jid}">Go back</a> and try again.'.format(jid=jid)

if __name__ == "__main__":
    app.run()
