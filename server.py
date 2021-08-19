# TODO return 503 if something doesn't update
from flask import Flask
from flask import request
from flask import jsonify
from flask import send_from_directory
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
        0x01: "PHONO",
        0x02: "AUX",
        0x03: "PVR",
        0x04: "AV",
        0x05: "STB",
        0x06: "CD",
        0x07: "BD",
        0x08: "SAT"
    }[source]


def str_to_source(source: str) -> bytes or None:
    return {
        "PHONO": 0x01,
        "AUX": 0x02,
        "PVR": 0x03,
        "AV": 0x04,
        "STB": 0x05,
        "CD": 0x06,
        "BD": 0x07,
        "SAT": 0x08
    }[source]


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
            return jsonify({
                "power": await state.get_power(use_state=False),
                "mute": await state.get_mute(use_state=False),
                "volume": await state.get_volume(use_state=False),
                "source": source_to_str(
                    await state.get_source(use_state=False)
                )
            })
    except Exception:
        return jsonify({
            "success": False,
        })

# Active high, assume 1 means on 0 means off


@app.route("/api/mute", methods=["POST"])
async def mute():
    value_to_bool = bool(int(request.args.get("value")))
    success = True
    client = Client(HOST_IP, HOST_PORT)
    try:
        async with ClientContext(client):
            state = State(client, ZONE)
            await state.set_mute(value_to_bool, use_rc5=False)
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
        async with ClientContext(client):
            state = State(client, ZONE)
            await state.set_volume(value_to_int)
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
    except Exception:
        success = False
    finally:
        return jsonify({
            "success": success
        })
