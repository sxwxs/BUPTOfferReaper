import os
import json
import time
import queue
import requests
import threading

import rsa
import buptgw
from flask import Flask, request, render_template, session, redirect, url_for

from models import Offer, Comment, Mark, db

app = Flask(__name__)


REPORT_URL_ENV_KEY = "DB_URI"

report_url = os.environ[REPORT_URL_ENV_KEY] if REPORT_URL_ENV_KEY in os.environ else ""

if report_url:
    def heart_beat_report():
        while True:
            r = requests.get(report_url)
            if r.text != 'ok':
                print('error heart beat report', r.text)
            time.sleep(500)
    t = threading.Thread(target=heart_beat_report)
    t.start()


def migrate_from_jl():
    data_list = []
    data_col = ['company', 'org', 'title', 'industry', 'location', 'salary', 'bonus', 'package', 'note', 'hukou', 'level',
                'type_', 'comments', 'key', 'time', 'difficulty']

    mark_list = []
    comment_list = []

    if os.path.exists('data.jl'):
        with open('data.jl', encoding='utf8') as f:
            for l in f:
                record = json.loads(l)
                if len(record) < len(data_col):
                    record += [''] * (len(data_col) - len(data_list))
                data_list.append(record)
                mark_list.append([0, 0])
                comment_list.append([])
        if os.path.exists('marks.log'):
            with open('marks.log', encoding='utf8') as f:
                for l in f:
                    i, x, _, _ = l.split('\t')
                    mark_list[int(i)][int(x)] += 1
        if os.path.exists('comments.log'):
            with open('comments.log', encoding='utf8') as f:
                for l in f:
                    i, x, _, _ = l.split('\t')
                    comment_list[int(i)].append(x)

        for old_id, d in enumerate(data_list):
            [company, org, title, industry, location, salary, bonus, package, note, hukou, level, type_, comments, key,
             created, difficulty] = d

            up_count = mark_list[old_id][0]
            down_count = mark_list[old_id][1]
            offer = Offer.create(company=company, org=org, title=title, industry=industry, location=location,
                                 salary=salary,
                                 bonus=bonus,
                                 package=package, note=note, hukou=hukou, level=level, type_=type_, comments=comments,
                                 key=key,
                                 created=created, difficulty=difficulty, up_count=up_count, down_count=down_count)

            user_comments = comment_list[old_id]
            for user_comment in user_comments:
                Comment.create(offer=offer, comment=user_comment, ip="", created=time.time())


@app.route('/')
def index():
    offers = list(Offer.select().execute())
    return render_template('index.html', offer_cnt=len(offers), status='正常', data_list=offers)


@app.route('/submit/')
def submit():
    return render_template('submit.html')


@app.route('/api/submit/', methods=['GET', 'POST'])
def submit_api():
    if request.method == 'POST':
        offer = Offer(company=request.form['company'],
                      org=request.form['org'],
                      title=request.form['title'],
                      industry=request.form['industry'],
                      location=request.form['location'],
                      salary=request.form['salary'],
                      bonus=request.form['bonus'],
                      package=request.form['package'],
                      note=request.form['note'],
                      hukou=request.form['hukou'],
                      level=request.form['level'],
                      type_=request.form['type'],
                      comments=request.form['comments'],
                      difficulty=request.form['difficulty'])
        key = request.form['key']

        if not key or not key.isdigit():  # 如果 key 为空或非法，则生成新的 key
            key, private = rsa.newkeys(512)
            assert key.e == 65537
            key = key.n
            n, e, d, p, q = private.n, private.e, private.d, private.p, private.q
            private_key='%d,%d,%d,%d,%d' % (n, e, d, p, q)
        else:
            key = int(key)
            private_key = ''

        offer.key = key
        offer.created = time.time()

        offer.save()

        return render_template('submit_result.html', public_key=str(key), private_key=private_key)
    return ''


@app.route('/view/<int:id_>/')
def view(id_):
    offer = Offer.get_by_id(id_)
    return render_template('view.html', offer=offer, id_=id_)


def get_ip():
    try:
        ip = request.headers['X-Forwarded-For'].split(',')[0]
    except:
        ip = request.remote_addr
    return ip


@app.route('/api/mark/<int:id_>/<int:x>/')
@db.atomic()
def mark(id_, x):
    assert x in [0, 1]
    ip = get_ip()

    offer = Offer.get_by_id(id_)
    Mark.create(offer=offer, mark=x, ip=ip, created=time.time())
    if x == 0:
        offer.up_count += 1
    else:
        offer.down_count += 1
    offer.save()
    return "成功！"


@app.route('/api/comment/<int:id_>/')
@db.atomic()
def comment(id_):
    comment = request.args.get('c', None)
    if len(comment) > 1000:
        return "评论长度不能大于 1000！"
    ip = get_ip()
    offer = Offer.get_by_id(id_)
    Comment.create(offer=offer, comment=comment, ip=ip, created=time.time())
    return "成功！"


if __name__ == '__main__':
    db.connect()
    db.create_tables([Offer, Comment, Mark])
    migrate_from_jl()
    app.run(host='127.0.0.1', port=12345)
