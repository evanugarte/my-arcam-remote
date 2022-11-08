import os

from flask import Flask
from flask import request
from flask import Response
from flask import jsonify

from arcam_state_handler import ArcamStateHandler
from arcam_metrics_handler import ArcamMetricsHandler
from message_announcer import MessageAnnouncer


app = Flask(__name__)

HOST_IP = os.getenv('HOST_IP')
HOST_PORT = os.getenv('HOST_PORT') or 50000
ZONE = os.getenv('ZONE') or 1
CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')

announcer = MessageAnnouncer()

state_handler = ArcamStateHandler(HOST_IP, HOST_PORT, ZONE)
metrics_handler = ArcamMetricsHandler()
metrics_handler.initialize()


@app.route("/api/health-check", methods=["GET"])
async def health_check():
    with metrics_handler.health_check_latency_seconds.time():
        health_check_response = await state_handler.health_check()
        if not health_check_response.get("success"):
            metrics_handler.network_errors.inc()
        return jsonify(health_check_response)


@app.route("/api/mute", methods=["POST"])
async def mute():
    value_to_bool = bool(int(request.args.get("value")))
    with metrics_handler.network_latency_seconds.time():
        mute_result = await state_handler.handle_mute(value_to_bool)
    if mute_result.get("success"):
        metrics_handler.mute_state.set(int(value_to_bool))
        announcer.push_message("mute", value_to_bool)
    else:
        metrics_handler.network_errors.inc()
    return jsonify(mute_result)


@app.route("/api/power", methods=["POST"])
async def power():
    value_to_bool = bool(int(request.args.get("value")))
    with metrics_handler.network_latency_seconds.time():
        power_result = await state_handler.handle_power(value_to_bool)
    if power_result.get("success"):
        metrics_handler.power_state.set(int(value_to_bool))
        announcer.push_message("power", value_to_bool)
    else:
        metrics_handler.network_errors.inc()
    return jsonify(power_result)


@app.route("/api/volume", methods=["POST"])
async def volume():
    value_to_int = int(request.args.get("value"))
    if value_to_int < 0 or value_to_int > 99:
        raise ValueError("Volume out of range")
    with metrics_handler.network_latency_seconds.time():
        volume_result = await state_handler.handle_volume(value_to_int)
    announcer.push_message("volume", value_to_int)
    if volume_result.get("success"):
        metrics_handler.volume_state.set(value_to_int)
    else:
        metrics_handler.network_errors.inc()
    return jsonify(volume_result)


@app.route("/api/source", methods=["POST"])
async def source():
    value = request.args.get('value')
    with metrics_handler.network_latency_seconds.time():
        source_result = await state_handler.handle_source(value)
    if source_result.get("success"):
        announcer.push_message("source", value)
    else:
        metrics_handler.network_errors.inc()
    return jsonify(source_result)

@app.route('/api/listen', methods=['GET'])
def listen():
    def stream():
        messages = announcer.listen()
        while True:
            msg = messages.get()
            yield msg
    return Response(stream(), mimetype='text/event-stream')

@app.route('/metrics')
def metrics():
    return Response(metrics_handler.generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
