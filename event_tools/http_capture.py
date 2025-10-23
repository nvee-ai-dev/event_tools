"""
Author: Martin

Date: 2025-09-22

License: Unlicense

Description:
    Flask application to capture POST events and save them to a file. Lots of help from various AIs.
    The goal was not to be "clever", but to be efficient and effective.
"""

from flask import Flask, request
import json
from datetime import datetime
from threading import Lock
from dotenv import dotenv_values
from pathlib import Path

config = dotenv_values(".env")

app = Flask(__name__)

# File goes in the specified directory, and is the current datetime
CAPTURE_PATH = config["CAPTURE_PATH"] or "events/"
now = datetime.now()
CAPTURE_FILE = now.strftime("%Y%m%d_%H%M%S")
JSON_FILE = Path(CAPTURE_PATH) / CAPTURE_FILE

file_lock = Lock()


def initialize_capture_file():
    """Initialize the capture file if it doesn't exist"""
    if not JSON_FILE:
        with open(JSON_FILE, "w") as f:
            json.dump(
                {"session_start": datetime.now().isoformat(), "events": []}, f, indent=2
            )


def append_event(event_data):
    """Append an event to the capture file"""
    with file_lock:
        # Read existing data
        with open(JSON_FILE, "r") as f:
            data = json.load(f)

        # Append new event
        data["events"].append(event_data)

        # Write back
        with open(JSON_FILE, "w") as f:
            json.dump(data, f, indent=2)


@app.route("/<path:path>", methods=["POST"])
def capture_all(path):
    timestamp = datetime.now().isoformat()

    # Capture request details
    captured = {
        "sequence": len(get_all_events()) + 1,  # Event number in sequence
        "timestamp": timestamp,
        "path": "/" + path,
        "method": request.method,
        "headers": dict(request.headers),
        "body": (
            request.get_json() if request.is_json else request.get_data(as_text=True)
        ),
        "query_params": dict(request.args) if request.args else None,
    }

    # Append to file
    append_event(captured)
    print(f"[{captured['sequence']}] Captured POST to /{path}")
    return {"status": "captured", "sequence": captured["sequence"]}, 200


@app.route("/capture/status", methods=["GET"])
def get_status():
    """Get capture status"""
    events = get_all_events()
    return {
        "total_events": len(events),
        "json_file": JSON_FILE,
        "session_start": get_session_start(),
    }, 200


@app.route("/capture/reset", methods=["POST"])
def reset_capture():
    """Reset/clear all captured events"""
    with file_lock:
        with open(JSON_FILE, "w") as f:
            json.dump(
                {"session_start": datetime.now().isoformat(), "events": []}, f, indent=2
            )

    print("Capture file reset")
    return {"status": "reset", "message": "All captured events cleared"}, 200


def get_all_events():
    """Helper to get all events"""
    try:
        with open(JSON_FILE, "r") as f:
            data = json.load(f)
            return data.get("events", [])
    except FileNotFoundError:
        return []


def get_session_start():
    """Helper to get session start time"""
    try:
        with open(JSON_FILE, "r") as f:
            data = json.load(f)
            return data.get("session_start")
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    initialize_capture_file()
    print(f"Capture server starting. Events will be saved to: {JSON_FILE}")
    print(f"Endpoints:")
    print(f"  - POST /<any-path>     : Capture request")
    print(f"  - GET /capture/status  : View capture status")
    print(f"  - POST /capture/reset  : Clear all captures")
    app.run(host="0.0.0.0", port=8000, debug=True)
