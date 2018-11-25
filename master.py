#!/usr/bin/env python3

from bottle import get, post, delete, run, request, response, static_file

import boto3
import json
import threading
import time
import validators

sqs       = boto3.resource('sqs')
queue_in  = sqs.get_queue_by_name(QueueName='queue-in')
queue_out = sqs.get_queue_by_name(QueueName='queue-out')

MAX_DEPTH       = None
discovered_urls = set()
workers         = []
edges           = []

class WaiterThread(threading.Thread):
    def __init__(self, delay=1):
        super().__init__()
        self.delay = delay
        self.stop_event = threading.Event()

    def run(self):
        while not self.is_stopped():
            for message in queue_out.receive_messages(MaxNumberOfMessages=10):
                msg = json.loads(message.body)
                prev_url = msg['source']
                url = msg['sink']
                depth = msg['depth']

                if url not in discovered_urls and validators.url(url) and (MAX_DEPTH is None or depth <= MAX_DEPTH):
                    out_msg = { 'url': url, 'depth': depth }
                    queue_in.send_message(MessageBody=json.dumps(out_msg))

                    print(f"### discovered new url {url} at depth {depth}")
                    discovered_urls.add(url)
                    edges.append((prev_url, url, depth))

                message.delete()

            time.sleep(self.delay)

    def stop(self):
        self.stop_event.set()

    def is_stopped(self):
        return self.stop_event.is_set()

wait = WaiterThread()

# called when a worker comes to life---consider also using a queue for this.
@post('/worker')
def register_new_worker():
    ip = request.environ.get('REMOTE_ADDR')
    workers.append(ip)
    response.status = 204

# ditto
@delete('/worker')
def deregister_worker():
    ip = request.environ.get('REMOTE_ADDR')
    workers.remove(ip)

# called when url is entered from the web frontend
@post('/crawl')
def start_crawl():
    url = request.forms.get('url')
    depth = int(request.forms.get('depth') or 10)

    global MAX_DEPTH
    MAX_DEPTH = depth

    print(f"starting crawl on {url}")
    msg = { 'url': url, 'depth': 0 }
    queue_in.send_message(MessageBody=json.dumps(msg))

    wait.start()

# try to stop a crawl process. note that purge can only happen every 60s
@delete('/crawl')
def stop_crawl():
    try:
        queue_in.purge()
        queue_out.purge()
    except:
        response.status = 400
        return

    global wait

    wait.stop()
    wait.join()
    wait = WaiterThread()

# queried to get progress. used by frontend to visualize
@get('/progress')
def get_progress():
    progress = { 'workers': workers, 'edges': edges }
    return json.dumps(progress)

# replace later with nginx or something
@get('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root='./static')

run(host='localhost', port=8080)
