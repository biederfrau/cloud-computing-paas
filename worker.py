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

sqs          = boto3.resource('sqs')
queue_in     = sqs.get_queue_by_name(QueueName='queue-in')
queue_out    = sqs.get_queue_by_name(QueueName='queue-out')
queue_master = sqs.get_queue_by_name(QueueName='queue-master')

print("sending hello to master")
random_id = str(uuid.uuid4())
queue_master.send_message(MessageBody=json.dumps({"kind": "hello", "id": random_id}))
atexit.register(lambda: queue_master.send_message(MessageBody=json.dumps({"kind": "bye", "id": random_id})))

while True:
    for message in queue_in.receive_messages(MaxNumberOfMessages=10, VisibilityTimeout=10):
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
            if href:
                # TODO better url handling
                if href.startswith('/'): href = url + href
                if not validators.url(href): continue

                msg = { 'source': url, 'sink': href, 'depth': depth + 1 }
                queue_out.send_message(MessageBody=json.dumps(msg))

        message.delete()

    time.sleep(5)
