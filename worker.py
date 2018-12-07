#!/usr/bin/env python3

from bs4 import BeautifulSoup

import atexit
import boto3
import json
import pretty
import requests
from requests.exceptions import MissingSchema
import sys
import time
import validators
import uuid
from urllib.parse import urlparse

sqs          = boto3.resource('sqs')
queue_in     = sqs.get_queue_by_name(QueueName='queue-in')
queue_out    = sqs.get_queue_by_name(QueueName='queue-out')
queue_master = sqs.get_queue_by_name(QueueName='queue-master')

print("sending hello to master")
random_id = str(uuid.uuid4())
queue_master.send_message(MessageBody=json.dumps({"kind": "hello", "id": random_id}))
atexit.register(lambda: queue_master.send_message(MessageBody=json.dumps({"kind": "bye", "id": random_id})))

while True:
    for message in queue_in.receive_messages(MaxNumberOfMessages=10, VisibilityTimeout=60):
        msg = json.loads(message.body)
        url = msg['url']
        depth = msg['depth']

        try:
            r = requests.get(url)
        except MissingSchema:
            continue

        links = BeautifulSoup(r.text, 'lxml').find_all('a')
        for link in links:
            href = link.get('href')
            if not href: continue

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
            msg = { 'source': url, 'sink': target, 'depth': depth + 1 }
            queue_out.send_message(MessageBody=json.dumps(msg))

        time.sleep(3)

        message.delete()
