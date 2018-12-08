import boto3
import json
import pretty
import requests
import re
import time
import validators
import socket
import os
import uuid
from urllib.parse import urlparse
from requests.exceptions import MissingSchema
from dynamodb.db_wrapper import DBWrapper


def consume_queue_in(event, context):
    sqs = boto3.resource('sqs')
    db = boto3.resource('dynamodb')
    queue_in = sqs.get_queue_by_name(QueueName='queue-in')
    queue_master = sqs.get_queue_by_name(QueueName='queue-master')

    lambda_id = socket.gethostname() + '_' + str(os.getpid()) + '_' + str(uuid.uuid4())
    print("sending hello to master from ", lambda_id)
    queue_master.send_message(MessageBody=json.dumps({"kind": "hello", "id": lambda_id}))

    dbw = DBWrapper(db)

    for record in event['Records']:
        print(record["body"])
        msg = json.loads(record["body"])
        url = msg['sink']
        depth = msg['depth']
        max_depth = msg['max_depth']

        if dbw.has_url_been_visited(url):
            continue

        print('here 1')

        try:
            r = requests.get(url)
        except MissingSchema as e:
            print('here 2')
            print(e)
            continue

        dbw.mark_url_as_visited(url)

        print('here 3')

        try:
            hrefs = re.findall(r'href=[\'"]?([^\'" >]+)', r.text)
        except:
            print('here 4')
            continue

        print('here 5')

        for href in hrefs:
            print(href)
            if not validators.url(href) and href != "./":  # try to fix
                if href.startswith('/'):  # root-relative url
                    parsed_parent = urlparse(url)
                    href = f"{parsed_parent.scheme}://{parsed_parent.netloc}{href}"
                else:  # relative url
                    href = url + ('' if url.endswith('/') else '/') + href

            if not validators.url(href):
                print(f"{pretty.red('!!!')} bad url: {href}")
                continue  # give up if attempts to fix did not work

            parsed_url = urlparse(href)
            target = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

            if url == target: continue  # ignore self-links (e.g. to anchors on page)

            dbw.add_url_to_webgraph(url, target, depth + 1)

            if depth + 1 < max_depth:
                msg = {'source': url, 'sink': target, 'depth': depth + 1, 'max_depth': max_depth}
                queue_in.send_message(MessageBody=json.dumps(msg))

    time.sleep(1)
    print("sending bye to master from ", lambda_id)
    queue_master.send_message(MessageBody=json.dumps({"kind": "bye", "id": lambda_id}))
