# from bs4 import BeautifulSoup
#
# import atexit
import boto3
# import json
# import pretty
# import requests
# from requests.exceptions import MissingSchema
# import validators
# import uuid
# from urllib.parse import urlparse



def consume_queue_in(event, context):
    sqs = boto3.resource('sqs')
    #queue_in = sqs.get_queue_by_name(QueueName='queue-in')
    queue_out = sqs.get_queue_by_name(QueueName='queue-out')
    queue_master = sqs.get_queue_by_name(QueueName='queue-master')

    # print("sending hello to master")
    # random_id = str(uuid.uuid4())
    # queue_master.send_message(MessageBody=json.dumps({"kind": "hello", "id": random_id}))
    # atexit.register(lambda: queue_master.send_message(MessageBody=json.dumps({"kind": "bye", "id": random_id})))

    queue_master.send_message(MessageBody="hello master!")
    queue_out.send_message(MessageBody="hello out!")

    # sqs = boto3.resource('sqs')
    # worker_feedback_queue = sqs.get_queue_by_name(QueueName='queue-out')
    # for record in event['Records']:
    #     url = record["body"]
    #     worker_feedback_queue.send_message(MessageBody=url)
    #     print('The URL is ', url)

    # for message in event['Records']:
    #     msg = json.loads(message.body)
    #     url = msg['url']
    #     depth = msg['depth']
    #
    #     try:
    #         r = requests.get(url)
    #     except MissingSchema:
    #         continue
    #
    #     links = BeautifulSoup(r.text, 'lxml').find_all('a')
    #     for link in links:
    #         href = link.get('href')
    #         if not href: continue
    #
    #         if not validators.url(href) and href != "./": # try to fix
    #             if href.startswith('/'): # root-relative url
    #                 href = url + href
    #             else: # relative url
    #                 href = url + ('' if url.endswith('/') else '/') + href
    #
    #         if not validators.url(href):
    #             print(f"{pretty.red('!!!')} bad url: {href}")
    #             continue # give up if attempts to fix did not work
    #
    #         parsed_url = urlparse(href)
    #         target = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    #
    #         if url == target: continue # ignore self-links (e.g. to anchors on page)
    #         msg = { 'source': url, 'sink': target, 'depth': depth + 1 }
    #         queue_out.send_message(MessageBody=json.dumps(msg))
    #
    #     message.delete()
