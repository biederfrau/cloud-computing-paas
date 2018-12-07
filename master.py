#!/usr/bin/env python3

import boto3
import json
import pretty

from bottle import get, post, delete, run, request, response, static_file, redirect, default_app
from polling_thread import PollingThread, WorkerPollingThread

sqs          = boto3.resource('sqs')
queue_in     = sqs.get_queue_by_name(QueueName='queue-in')
queue_out    = sqs.get_queue_by_name(QueueName='queue-out')
queue_master = sqs.get_queue_by_name(QueueName='queue-master')

work = WorkerPollingThread(queue_master)
poll = PollingThread(queue_in, queue_out)

work.start()
poll.start()

# called when url is entered from the web frontend
@post('/crawl')
def start_crawl():
    url = request.forms.get('url')
    depth = int(request.forms.get('depth') or 10)

    print(f"{pretty.green('###')} starting crawl on {url}")
    msg = { 'url': url, 'depth': 0, 'max_depth': depth }
    queue_in.send_message(MessageBody=json.dumps(msg))

    global poll

    poll.stop()
    poll.join()

    poll = PollingThread(queue_in, queue_out)
    poll.set_depth(depth)
    poll.add_root(url)

    poll.start()

# try to stop a crawl process. note that purge can only happen every 60s
@delete('/crawl')
def stop_crawl():
    print(f"{pretty.green('###')} trying to stop crawl")
    try:
        queue_in.purge()
        queue_out.purge()
    except:
        print(f"{pretty.red('!!!')} could not purge queues")
        response.status = 400
        return

# queried to get progress. used by frontend to visualize
@get('/progress')
def get_progress():
    progress = { 'workers': work.workers(), 'edges': poll.edges() }
    return json.dumps(progress)

@get('/progress/workers')
def get_progress_workers():
    progress = { 'workers': work.workers() }
    return json.dumps(progress)

@get('/progress/edges')
def get_progress_edges():
    progress = { 'edges': poll.edges()  }
    return json.dumps(progress)

@get('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root='./static')

@get('/')
def redirect_index():
    redirect('/static/index.html')

application = default_app() # this is needed by the EB WSGI
run(host='localhost', port=8080)
