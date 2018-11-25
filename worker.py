#!/usr/bin/env python3

from bs4 import BeautifulSoup

import boto3
import requests
from requests.exceptions import MissingSchema
import sys
import validators

import json
import time
import atexit

sqs       = boto3.resource('sqs')
queue_in  = sqs.get_queue_by_name(QueueName='queue-in')
queue_out = sqs.get_queue_by_name(QueueName='queue-out')

with open('.master') as f:
    MASTER = f.readline().strip()
    print(f"master is at {MASTER}")

r = requests.post(f"{MASTER}/worker")
if r.status_code != 204:
    print("BAD")
    sys.exit()

atexit.register(lambda: requests.delete(f"{MASTER}/worker"))

while True:
    for message in queue_in.receive_messages(MaxNumberOfMessages=2, VisibilityTimeout=10):
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

                print(f"### pushing valid url {href} at depth {depth+1}")
                msg = { 'source': url, 'sink': href, 'depth': depth + 1 }
                queue_out.send_message(MessageBody=json.dumps(msg))

        message.delete()

    time.sleep(5)
