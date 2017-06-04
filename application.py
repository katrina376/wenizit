from flask import Flask, render_template, request
app = Flask(__name__)

import json
import re

data_list = []
with open('list.txt') as f:
    for line in f:
        data_list.append(line.strip())

regexp = r'([\d同一二三四五六七八九十]+年[、同某\d一二三四五六七八九十零]*月[初間某\d卅廿一二三四五六七八九十零]+日?)(?!\d+年\d+月\d+日)'

@app.route('/')
@app.route('/<filename>')
def index(filename=None):
    if filename in data_list:
        with open('data/{filename}.json'.format(filename=filename), 'r') as f:
            string = f.read()
            book = json.loads(string)
            title = book['title']
            raw = book['content']
            date = book['commit_date']

            split = re.split(regexp, raw)
            content = []
            count_of_date = 0
            for text in split:
                if re.match(regexp, text) is not None:
                    count_of_date += 1
                    if text == date:
                        content.append({'text': text, 'is_date': True, 'chosen': True})
                    else:
                        content.append({'text': text, 'is_date': True, 'chosen': False})
                else:
                    content.append({'text': text, 'is_date': False, 'chosen': False})

            return render_template('template.html',
                                    content=content,
                                    title=title,
                                    date=date,
                                    count_of_date=count_of_date,
                                    filename=filename)
    else:
        return 'Filename does not exist: {filename}'.format(filename=filename)

@app.route('/<filename>/save', methods=['POST'])
def save(filename=None):
    if filename in data_list:
        try:
            date = request.form['chosen']
            with open('data/{filename}.json'.format(filename=filename), 'r') as f:
                string = f.read()
                book = json.loads(string)

            with open('data/{filename}.json'.format(filename=filename), 'w') as f:
                book['commit_date'] = date if date is not None else ''
                f.write(json.dumps(book, ensure_ascii=False))

            next_file_idx = data_list.index(filename) + 1
            if next_file_idx < len(data_list):
                next_filename = data_list[next_file_idx]
                return 'Ok! Take off for the next one: <a href="/{filename}">{filename}</a>'.format(filename=next_filename)
            else:
                return 'Ok! This is the end of the stack.'
        except:
            return 'Something went wrong. <a href="/{filename}">Go back</a> and try again.'.format(filename=filename)
    else:
        return 'Filename does not exist: {filename}'.format(filename=filename)
