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
from event_tools.file_manager import FileManager


config = dotenv_values(".env")

app = Flask(__name__)

# File goes in the specified directory, and is the current datetime
CAPTURE_PATH = config["CAPTURE_PATH"] or "./events"
now = datetime.now()
CAPTURE_TIME = datetime.now().strftime("%Y%m%d_%H%M%S")
JSON_FILE = FileManager(CAPTURE_PATH, f"{CAPTURE_TIME}.json")
session_start = "Not started"

file_lock = Lock()

# Module scope events record and last write time
# Constant define write frequency and max events to accumulate before writing.
# This behaviour effectively emulates AWS FireHose behaviout
MAX_TIME_BETWEEN_WRITES = 2  # seconds
MAX_ACCUMULATED_EVENTS_BEFORE_WRITE = 1000
events_list = []
total_events = 0
last_write_time = datetime.now()


def initialize_capture():
    """Initialize the capture file if it doesn't exist"""
    global total_events, last_write_time, session_start

    events_list.clear()
    total_events = 0
    last_write_time = datetime.now()
    session_start = last_write_time.isoformat()
    with file_lock:
        JSON_FILE.dump({"session_start": session_start, "events": []}, indent=2)


def write_events() -> None:
    global last_write_time

    if (
        len(events_list) >= MAX_ACCUMULATED_EVENTS_BEFORE_WRITE
        or (datetime.now() - last_write_time).total_seconds() >= MAX_TIME_BETWEEN_WRITES
    ):
        with file_lock:
            # Read existing data
            data = JSON_FILE.load()

            # Append new events
            for event in events_list:
                data["events"].append(event)

            # Write back, zero the timer, empty the events list
            JSON_FILE.dump(data, indent=2)
            last_write_time = datetime.now()
            events_list.clear()


def append_event(event_data):
    """Append an event to the capture file"""
    global total_events

    events_list.append(event_data)
    total_events += 1
    write_events()


@app.route("/<path:path>", methods=["POST"])
def capture_all(path):
    timestamp = datetime.now().isoformat()

    # Capture request details
    captured = {
        "sequence": total_events + 1,  # Event number in sequence
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
    return {
        "total_events": total_events,
        "json_file": JSON_FILE,
        "session_start": session_start,
    }, 200


@app.route("/capture/reset", methods=["POST"])
def reset_capture():
    """Reset/clear all captured events"""
    initialize_capture()
    print("Capture file reset")
    return {"status": "reset", "message": "All captured events cleared"}, 200


if __name__ == "__main__":
    initialize_capture()
    print(f"Capture server starting. Events will be saved to: {JSON_FILE}")
    print(f"Endpoints:")
    print(f"  - POST /<any-path>     : Capture request")
    print(f"  - GET /capture/status  : View capture status")
    print(f"  - POST /capture/reset  : Clear all captures")
    app.run(host="0.0.0.0", port=8000, debug=True)
