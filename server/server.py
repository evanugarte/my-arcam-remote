# TODO return 503 if something doesn't update
import json
import queue
import os

from flask import Flask
from flask import request
from flask import Response
from flask import jsonify
from flask import send_from_directory
from prometheus_client import start_http_server
from prometheus_client import Histogram

from arcam_state_handler import ArcamStateHandler


app = Flask(__name__)

HOST_IP = os.getenv('HOST_IP')
HOST_PORT = os.getenv('HOST_PORT') or 50000
ZONE = os.getenv('ZONE') or 1

# rate(request_latency_seconds_sum[1m]) / rate(request_latency_seconds_count[1m])
health_check_latency_seconds = Histogram(
    'health_check_latency_seconds', 'Time spent processing health check'
)

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

announcer = MessageAnnouncer()

def format_sse(field, value, event=None):
    msg = f'data: {json.dumps({field: value})}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg

def push_message(field, value):
    msg = format_sse(field, value)
    announcer.announce(msg)


@app.route("/", methods=["GET"])
async def base():
    return send_from_directory("website/public", "index.html")


@app.route("/<path:path>")
def home(path):
    return send_from_directory("website/public", path)


@app.route("/api/health-check", methods=["GET"])
async def health_check():
    a = ArcamStateHandler(HOST_IP, HOST_PORT, ZONE)
    return jsonify(await a.health_check())


@app.route("/api/mute", methods=["POST"])
async def mute():
    value_to_bool = bool(int(request.args.get("value")))
    a = ArcamStateHandler(HOST_IP, HOST_PORT, ZONE)
    mute_result = await a.handle_mute(value_to_bool)
    if mute_result.get("success"):
        push_message("mute", value_to_bool)
    return jsonify(mute_result)


@app.route("/api/power", methods=["POST"])
async def power():
    value_to_bool = bool(int(request.args.get("value")))
    a = ArcamStateHandler(HOST_IP, HOST_PORT, ZONE)
    power_result = await a.handle_power(value_to_bool)
    if power_result.get("success"):
        push_message("power", value_to_bool)
    return jsonify(power_result)


@app.route("/api/volume", methods=["POST"])
async def volume():
    value_to_int = int(request.args.get("value"))
    if value_to_int < 0 or value_to_int > 99:
        raise ValueError("Volume out of range")
    a = ArcamStateHandler(HOST_IP, HOST_PORT, ZONE)
    volume_result = await a.handle_volume(value_to_int)
    if volume_result.get("success"):
        push_message("volume", value_to_int)
    return jsonify(volume_result)


@app.route("/api/source", methods=["POST"])
async def source():
    value = request.args.get('value')
    a = ArcamStateHandler(HOST_IP, HOST_PORT, ZONE)
    source_result = await a.handle_source(value)
    if source_result.get("success"):
        push_message("source", value)
    return jsonify(source_result)

@app.route('/api/listen', methods=['GET'])
def listen():
    def stream():
        messages = announcer.listen()
        while True:
            msg = messages.get()
            yield msg
    return Response(stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    start_http_server(50052)
    app.run(host='0.0.0.0')
