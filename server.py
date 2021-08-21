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

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=False, processes=10)
