#!/usr/bin/env python3

import boto3
from boto3.dynamodb.conditions import Key

class DBWrapper():
    def __init__(self, DB):
        self._DB = DB
        self._visited_urls = DB.Table('visited_urls')
        self._edges = DB.Table('edges')

    def url_visited(self, url):
        r = self._visited_urls.get_item(Key={'url': url})
        return 'Item' in r

    def store_url(self, url):
        self._visited_urls.put_item(TableName='visited_urls', Item={'url': url})

    def store_edge(self, source, sink, depth=0):
        self._edges.put_item(Item={'source_sink': f"{source}_{sink}", 'source': source, 'sink': sink, 'depth': depth})

    def get_urls(self):
        return self._visited_urls.scan()['Items']

    def get_edges(self):
        return self._edges.scan()['Items']

    def clear(self):
        r = self._visited_urls.scan(ProjectionExpression='#k', ExpressionAttributeNames={'#k': 'url'})
        with self._visited_urls.batch_writer() as batch:
            for url in r['Items']:
                batch.delete_item(Key=url)

        r = self._edges.scan(ProjectionExpression='#k', ExpressionAttributeNames={'#k': 'source_sink'})
        with self._edges.batch_writer() as batch:
            for source_sink in r['Items']:
                batch.delete_item(Key=source_sink)
