import json
import pretty
import threading


class WorkerPollingThread(threading.Thread):
    def __init__(self, queue, delay=1):
        super().__init__()
        self._delay = delay
        self._queue = queue
        self._workers = set()

    def run(self):
        while True:
            for message in self._queue.receive_messages(MaxNumberOfMessages=1):
                msg = json.loads(message.body)

                kind = msg['kind']
                worker_id = msg['id']

                if kind == "hello":
                    self._workers.add(worker_id)
                    print(f"{pretty.green('###')} new worker: {worker_id}")
                elif kind == "bye":
                    try:
                        self._workers.discard(worker_id)
                        print(f"{pretty.green('###')} worker left: {worker_id}")
                    except ValueError:
                        pass # not in list does not matter

                message.delete()

    def workers(self):
        return list(self._workers)

    def clear(self):
        self._workers = set()
