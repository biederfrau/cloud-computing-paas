#!/usr/bin/env python3

import boto3
import json
import pretty

from bottle import get, post, delete, run, request, response, static_file, redirect, default_app
from polling_thread import WorkerPollingThread
from dynamodb.db_wrapper import DBWrapper

sqs          = boto3.resource('sqs')
db           = boto3.resource('dynamodb')
queue_in     = sqs.get_queue_by_name(QueueName='queue-in-testing')
queue_master = sqs.get_queue_by_name(QueueName='queue-master-testing')

dbw = DBWrapper(db)
work = WorkerPollingThread(queue_master)

work.start()

# called when url is entered from the web frontend
@post('/crawl')
def start_crawl():
    url = request.forms.get('url')
    depth = int(request.forms.get('depth') or 10)

    print(f"{pretty.green('###')} starting crawl on {url}")
    msg = { 'sink': url, 'depth': 0, 'max_depth': depth }
    queue_in.send_message(MessageBody=json.dumps(msg))

# try to stop a crawl process. note that purge can only happen every 60s
@delete('/crawl')
def stop_crawl():
    print(f"{pretty.green('###')} trying to stop crawl")
    try:
        dbw.clear()
        queue_in.purge()
    except:
        print(f"{pretty.red('!!!')} could not purge queues")
        response.status = 400
        return

# queried to get progress. used by frontend to visualize
@get('/progress')
def get_progress():
    queue_in.load()
    edges = [(r['source'], r['sink'], int(r['depth'])) for r in dbw.get_edges()]
    progress = { 'workers': work.workers(), 'edges': edges, 'nodes': dbw.get_urls(),'n': queue_in.attributes['ApproximateNumberOfMessages'] }
    return json.dumps(progress)

@get('/progress/workers')
def get_progress_workers():
    progress = { 'workers': work.workers() }
    return json.dumps(progress)

@get('/progress/edges')
def get_progress_edges():
    edges = [(r['source'], r['sink'], int(r['depth'])) for r in dbw.get_edges()]
    progress = { 'edges': edges  }
    return json.dumps(progress)

@get('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root='./static')

@get('/')
def redirect_index():
    redirect('/static/index.html')

application = default_app() # this is needed by the EB WSGI
if __name__ == '__main__':
    run(host='localhost', port=8080)
