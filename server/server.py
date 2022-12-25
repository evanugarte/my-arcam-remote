import argparse
import os

from flask import Flask
from flask import request
from flask import Response
from flask import jsonify
from flask_cors import CORS

from arcam_state_handler import ArcamStateHandler
from arcam_metrics_handler import ArcamMetricsHandler
from constants import DeviceMetric
from message_announcer import MessageAnnouncer


app = Flask(__name__)
CORS(app)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--device_ip",
    required=True,
    help="The IP address of the Arcam device"
)
parser.add_argument(
    "--device_port",
    type=int,
    default=50000,
    help="Network port of the Arcam device to send commands to, defaults to 50000."
)
parser.add_argument(
    "--device_zone",
    type=int,
    default=1,
    help="Zone of the Arcam device to send commands to, defaults to 1."
)

args = parser.parse_args()

CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')

announcer = MessageAnnouncer()

state_handler = ArcamStateHandler(args.device_ip, args.device_port, args.device_zone)
metrics_handler = ArcamMetricsHandler()
metrics_handler.initialize()


@app.route("/health-check", methods=["GET"])
async def health_check():
    with metrics_handler.health_check_latency_seconds.time():
        health_check_response = await state_handler.health_check()
        if not health_check_response.get("success"):
            metrics_handler.network_errors.inc()
        return jsonify(health_check_response)


@app.route("/set/<metric>", methods=["POST"])
async def update_device(metric=""):
    try:
        # assuming metric is always a string type so upper()
        # will not raise an AttributeError
        metric_as_enum = DeviceMetric[metric.upper()]
        cast_value =  metric_as_enum.cast_to_correct_type(request.args.get("value"))
        if not metric_as_enum.is_valid(cast_value):
            raise ValueError(f"{cast_value} is an invalid value for metric {metric}")
        with metrics_handler.network_latency_seconds.time():
            result = await state_handler.set_metric(metric_as_enum, cast_value)
        if result.get("success"):
            metrics_handler.maybe_update_gauge_with_enum(metric_as_enum, cast_value)
            announcer.push_message(metric_as_enum.designation, cast_value)
        else:
            metrics_handler.network_errors.inc()
        return jsonify(result)
    except KeyError:
        return Response(
            f"\"{metric}\" is not a supported metric for updating Arcam state.",
            status=400,
            mimetype="text/plain",
        )
    except ValueError as e:
        return Response(repr(e), status=400, content_type="text/plain")

@app.route("/listen", methods=["GET"])
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
