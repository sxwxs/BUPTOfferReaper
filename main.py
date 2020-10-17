import os
import json
import time
import queue
import threading

import rsa
from flask import Flask, request, render_template, session, redirect, url_for


app = Flask(__name__)


data_list = []
data_col = ['company', 'org', 'title', 'industry,location', 'salary', 'bonus', 'package', 'note', 'hukou', 'level', 'type_', 'comments', 'key', 'time', 'difficulty']

mark_list = []
comment_list = []
mark_queue = queue.Queue()
comment_queue = queue.Queue()
write_record_queue = queue.Queue()

if os.path.exists('data.jl'):
    with open('data.jl', encoding='utf8') as f:
        for l in f:
            record = json.loads(l)
            if len(record) < len(data_col):
                record += [''] * (len(data_col)-len(data_list))
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

def write_record_thread():
    while True:
        r = write_record_queue.get()
        with open('data.jl', 'a', encoding='utf8') as f:
            f.write(r)

def mark_thread():
    while True:
        i, x, ip = mark_queue.get()
        if i < len(mark_list):
            mark_list[i][x] += 1
        with open('marks.log', 'a', encoding='utf8') as f:
            f.write('%d\t%d\t%s\t%d\n' % (i, x, ip, int(time.time())))
        
def comment_thread():
    while True:
        i, x, ip = comment_queue.get()
        if i < len(comment_list):
            comment_list[i].append(x)
        with open('comments.log', 'a', encoding='utf8') as f:
            f.write('%d\t%s\t%s\t%d\n' % (i, x, ip, int(time.time())))

t1 = threading.Thread(target=write_record_thread)
t2 = threading.Thread(target=mark_thread)
t3 = threading.Thread(target=comment_thread)
t1.start()
t2.start()
t3.start()

@app.route('/yPmgNXW/')
def status():
    return str(t1) + str(t2) + str(t3)

@app.route('/')
def index():
    return render_template('index.html', offer_cnt=len(data_list) , status='正常', data_list=data_list)

@app.route('/submit/')
def submit():
    return render_template('submit.html')
    
@app.route('/api/submit/', methods=['GET', 'POST'])
def submit_api():
    if request.method == 'POST':
        company = request.form['company']
        org = request.form['org']
        title = request.form['title']
        industry = request.form['industry']
        location = request.form['location']
        salary = request.form['salary']
        bonus = request.form['bonus']
        package = request.form['package']
        note = request.form['note']
        hukou = request.form['hukou']
        level = request.form['level']
        type_ = request.form['type']
        comments = request.form['comments']
        key = request.form['key']
        difficulty = request.form['difficulty']
        if not key or not key.isdigit(): # 如果 key 为空或非法，则生成新的 key
            key, private = rsa.newkeys(512)
            assert key.e == 65537
            key = key.n
            n, e, d, p, q = private.n, private.e, private.d, private.p, private.q
        else:
            key = int(key)
            n, e, d, p, q = '', '', '', '', ''
        record = [company, org, title,industry,location, salary, bonus, package, note, hukou, level, type_, comments, key, time.time(), difficulty]
        record_str = json.dumps(record, ensure_ascii=False) + '\n'
        write_record_queue.put(record_str)
        mark_list.append([0, 0])
        comment_list.append([])
        data_list.append(record)
        return render_template('submit_result.html', public_key=str(key), private_key='%d,%d,%d,%d,%d' % (n, e, d, p, q))
    else:
        return ''

@app.route('/view/<int:id_>/')
def view(id_):
    return render_template('view.html', info=data_list[id_], comment=comment_list[id_], mark=mark_list[id_], id_=id_)

def get_ip():
    try:
        ip = request.headers['X-Forwarded-For'].split(',')[0]
    except:
        ip = request.remote_addr
    return ip

@app.route('/api/mark/<int:id_>/<int:x>/')
def mark(id_, x):
    assert x in [0, 1]
    ip = get_ip()
    mark_queue.put((id_, x, ip))
    return "成功！"

@app.route('/api/comment/<int:id_>/')
def comment(id_):
    comment = request.args.get('c', None)
    if len(comment) > 1000:
        return "评论长度不能大于 1000！"
    ip = get_ip()
    comment_queue.put((id_, comment, ip))
    return "成功！"

if __name__=='__main__':
    app.run(host='127.0.0.1', port=12345)
