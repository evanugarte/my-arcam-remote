# TODO return 503 if something doesn't update
from flask import Flask
from flask import request
from flask import Response
from flask import jsonify
from flask import send_from_directory
import json
import queue
import os

from arcam_fmj.src.arcam.fmj import SA10SourceCodes
from arcam_fmj.src.arcam.fmj.client import Client
from arcam_fmj.src.arcam.fmj.client import ClientContext
from arcam_fmj.src.arcam.fmj.state import State

app = Flask(__name__)

HOST_IP = os.getenv('HOST_IP')
HOST_PORT = os.getenv('HOST_PORT') or 50000
ZONE = os.getenv('ZONE') or 1


def source_to_str(source: bytes) -> str or None:
    return {
        SA10SourceCodes.PHONO: "PHONO",
        SA10SourceCodes.AUX: "AUX",
        SA10SourceCodes.PVR: "PVR",
        SA10SourceCodes.AV: "AV",
        SA10SourceCodes.STB: "STB",
        SA10SourceCodes.CD: "CD",
        SA10SourceCodes.BD: "BD",
        SA10SourceCodes.SAT: "SAT"
    }[source]


def str_to_source(source: str) -> bytes or None:
    return {
        "PHONO": SA10SourceCodes.PHONO,
        "AUX": SA10SourceCodes.AUX,
        "PVR": SA10SourceCodes.PVR,
        "AV": SA10SourceCodes.AV,
        "STB": SA10SourceCodes.STB,
        "CD": SA10SourceCodes.CD,
        "BD": SA10SourceCodes.BD,
        "SAT": SA10SourceCodes.SAT
    }[source]

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
    client = Client(HOST_IP, HOST_PORT)
    try:
        async with ClientContext(client):
            state = State(client, ZONE)
            power = await state.get_power(use_state=False),
            mute = await state.get_mute(use_state=False),
            volume = await state.get_volume(use_state=False),
            source = source_to_str(
                    await state.get_source(use_state=False)
                )
            await client.stop()
            return jsonify({
                "power": power[0],
                "mute": mute[0],
                "volume": volume[0],
                "source": source
            })
    except Exception:
        return jsonify({
            "success": False,
        })


@app.route("/api/mute", methods=["POST"])
async def mute():
    value_to_bool = bool(int(request.args.get("value")))
    success = True
    client = Client(HOST_IP, HOST_PORT)
    try:
        async with ClientContext(client):
            state = State(client, ZONE)
            await state.set_mute(value_to_bool, use_rc5=False)
            await client.stop()
            push_message("mute", value_to_bool)
    except Exception:
        success = False
    finally:
        return jsonify({
            "success": success
        })


@app.route("/api/power", methods=["POST"])
async def power():
    value_to_bool = bool(int(request.args.get("value")))
    success = True
    client = Client(HOST_IP, HOST_PORT)
    try:
        async with ClientContext(client):
            state = State(client, ZONE)
            await state.set_power(value_to_bool, use_rc5=False)
            await client.stop()
            push_message("power", value_to_bool)
    except Exception:
        success = False
    finally:
        return jsonify({
            "success": success
        })


@app.route("/api/volume", methods=["POST"])
async def volume():
    value_to_int = int(request.args.get("value"))
    success = True
    client = Client(HOST_IP, HOST_PORT)
    try:
        if value_to_int < 0 or value_to_int > 99:
            raise ValueError("Volume out of range")
        async with ClientContext(client):
            state = State(client, ZONE)
            await state.set_volume(value_to_int)
            await client.stop()
            push_message("volume", value_to_int)
    except Exception:
        success = False
    finally:
        return jsonify({
            "success": success
        })


@app.route("/api/source", methods=["POST"])
async def source():
    value = request.args.get('value')
    success = True
    client = Client(HOST_IP, HOST_PORT)
    try:
        async with ClientContext(client):
            state = State(client, ZONE)
            await state.set_source(str_to_source(value), use_rc5=False)
            await client.stop()
            push_message("source", value)
    except Exception:
        success = False
    finally:
        return jsonify({
            "success": success
        })

@app.route('/api/listen', methods=['GET'])
def listen():
    def stream():
        messages = announcer.listen()
        while True:
            msg = messages.get()
            yield msg
    return Response(stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
