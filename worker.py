#!/usr/bin/env python3

import atexit
import boto3
import json
import pretty
import requests
import re
from requests.exceptions import MissingSchema
import time
import validators
import uuid
from urllib.parse import urlparse

from dynamodb.db_wrapper import DBWrapper

sqs          = boto3.resource('sqs')
db           = boto3.resource('dynamodb')
queue_in     = sqs.get_queue_by_name(QueueName='queue-in-testing')
queue_master = sqs.get_queue_by_name(QueueName='queue-master-testing')

print("sending hello to master")
random_id = str(uuid.uuid4())
queue_master.send_message(MessageBody=json.dumps({"kind": "hello", "id": random_id}))
atexit.register(lambda: queue_master.send_message(MessageBody=json.dumps({"kind": "bye", "id": random_id})))

dbw = DBWrapper(db)

while True:
    for message in queue_in.receive_messages(MaxNumberOfMessages=10, VisibilityTimeout=60):
        msg       = json.loads(message.body)
        url       = msg['sink']
        depth     = msg['depth']
        max_depth = msg['max_depth']

        try:
            r = requests.get(url)
        except MissingSchema:
            message.delete()
            continue

        if dbw.url_visited(url):
            message.delete()
            continue

        hrefs = re.findall(r'href=[\'"]?([^\'" >]+)', r.text)

        print(url)
        for href in hrefs:
            if not validators.url(href) and href != "./": # try to fix
                if href.startswith('/'): # root-relative url
                    parsed_parent = urlparse(url)
                    href = f"{parsed_parent.scheme}://{parsed_parent.netloc}{href}"
                else: # relative url
                    href = url + ('' if url.endswith('/') else '/') + href

            if not validators.url(href):
                print(f"{pretty.red('!!!')} bad url: {href}")
                message.delete()
                continue # give up if attempts to fix did not work

            parsed_url = urlparse(href)
            target = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

            if url == target: continue # ignore self-links (e.g. to anchors on page)

            dbw.store_edge(url, target, depth + 1)
            dbw.store_url(url)

            if depth + 1 < max_depth:
                msg = { 'source': url, 'sink': target, 'depth': depth + 1, 'max_depth': max_depth }
                queue_in.send_message(MessageBody=json.dumps(msg))

        message.delete()
        time.sleep(3)
