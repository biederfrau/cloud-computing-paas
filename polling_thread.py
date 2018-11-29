#!/usr/bin/env python3

import json
import pretty
import threading
import time

class PollingThread(threading.Thread):
    def __init__(self, queue_in, queue_out, delay=1, depth=1):
        super().__init__()
        self._delay = delay
        self._stop_event = threading.Event()

        self._queue_in = queue_in
        self._queue_out = queue_out

        self._depth = depth
        self._discovered_urls = set()
        self._edges = []

    def run(self):
        while not self.is_stopped():
            for message in self._queue_out.receive_messages(MaxNumberOfMessages=10):
                msg = json.loads(message.body)
                prev_url = msg['source']
                url = msg['sink']
                depth = msg['depth']

                if url not in self._discovered_urls and depth <= self._depth:
                    out_msg = { 'url': url, 'depth': depth }
                    self._queue_in.send_message(MessageBody=json.dumps(out_msg))

                    print(pretty.green(f"### discovered new url {url} at depth {depth}"))
                    self._discovered_urls.add(url)
                    self._edges.append((prev_url, url, depth))

                message.delete()

            time.sleep(self._delay)

    def stop(self):
        self._stop_event.set()

    def restart(self):
        self._stop_event.clear()

    def is_stopped(self):
        return self._stop_event.is_set()

    def edges(self):
        return self._edges

    def urls(self):
        return self._discovered_urls

    def depth(self):
        return self._depth

    def set_depth(self, depth):
        self._depth = depth

class WorkerPollingThread(threading.Thread):
    def __init__(self, queue, delay=1):
        super().__init__()
        self._delay = delay
        self._queue = queue
        self._workers = []

    def run(self):
        while True:
            for message in self._queue.receive_messages(MaxNumberOfMessages=1):
                msg = json.loads(message.body)

                kind = msg['kind']
                worker_id = msg['id']

                if kind == "hello":
                    self._workers.append(worker_id)
                    print(f"{pretty.green('###')} new worker: {worker_id}")
                elif kind == "bye":
                    try:
                        self._workers.remove(worker_id)
                        print(f"{pretty.green('###')} worker left: {worker_id}")
                    except ValueError:
                        pass # not in list does not matter

    def workers(self):
        return self._workers
