import os

from flask import Flask
from flask import request
from flask import Response
from flask import jsonify
from flask import send_from_directory
from prometheus_client import start_http_server
from prometheus_client import Histogram

from arcam_command_queue import ArcamCommandQueue
from arcam_metrics_handler import ArcamMetricsHandler
from arcam_state_handler import ArcamStateHandler
from message_announcer import MessageAnnouncer
from constants import ModifierType


app = Flask(__name__)

HOST_IP = os.getenv('HOST_IP')
HOST_PORT = os.getenv('HOST_PORT') or 50000
ZONE = os.getenv('ZONE') or 1

announcer = MessageAnnouncer()

state_handler = ArcamStateHandler(HOST_IP, HOST_PORT, ZONE)

command_queue = ArcamCommandQueue(state_handler, announcer)
command_queue.initialize()

metrics_handler = ArcamMetricsHandler()
metrics_handler.initialize()

@app.route("/", methods=["GET"])
async def base():
    return send_from_directory("website/public", "index.html")


@app.route("/<path:path>")
def home(path):
    return send_from_directory("website/public", path)


@app.route("/api/health-check", methods=["GET"])
async def health_check():
    with metrics_handler.health_check_latency_seconds.time():
        return jsonify(await state_handler.health_check())


@app.route("/api/mute", methods=["POST"])
async def mute():
    value_to_bool = bool(int(request.args.get("value")))
    command_queue.push_to_queue(ModifierType.MUTE, value_to_bool)
    return jsonify({"what": 9999})


@app.route("/api/power", methods=["POST"])
async def power():
    value_to_bool = bool(int(request.args.get("value")))
    command_queue.push_to_queue(ModifierType.POWER, value_to_bool)
    return jsonify({"what": 9999})


@app.route("/api/volume", methods=["POST"])
async def volume():
    value_to_int = int(request.args.get("value"))
    if value_to_int < 0 or value_to_int > 99:
        raise ValueError("Volume out of range")
    command_queue.push_to_queue(ModifierType.VOLUME, value_to_int)
    return jsonify({"what": 9999})


@app.route("/api/source", methods=["POST"])
async def source():
    value = request.args.get('value')
    command_queue.push_to_queue(ModifierType.SOURCE, value)
    return jsonify({"what": 9999})

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
