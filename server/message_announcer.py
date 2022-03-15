import json
import queue


class MessageAnnouncer:
    def __init__(self):
        self.listeners = []

    def listen(self):
        q = queue.Queue(maxsize=5)
        self.listeners.append(q)
        self.listeners[-1].put_nowait(f'data=You have successfully connected.\n\n')
        return q

    def announce(self, msg):
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]

    def format_sse(self, field, value, event=None):
        msg = f'data: {json.dumps({field: value})}\n\n'
        if event is not None:
            msg = f'event: {event}\n{msg}'
        return msg

    def push_message(self, field, value):
        msg = self.format_sse(field, value)
        self.announce(msg)
