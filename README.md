# Event Tools
A collection of tools to capture and replay HTTP events/traffic

## HTTP Capture (`http_capture.py`)
This is a Flask based app. If you direct POSTS at it, it will capture them and store them in a JSON file. They can be replayed in sequence and with the relative timing preserved. 

To use:
- configure the capture file and path in the .env filew, e.g.:
```
# .env contains settings and values used in the Event Tools project
CAPTURE_PATH=events/
CAPTURE_FILE=events-2025-10-22.json
```

Then run the capture app
```sh
poetry run python event_tools/http_capture.py
```

The capture event offers two control endpoints:
- one to show status
- one to clear the captured events

A full run is shown below
```sh
martin@Martins-M3-Max event_tools % poetry run python event_tools/http_capture.py
Capture server starting. Events will be saved to: events-2025-10-22.json
Endpoints:
  - POST /<any-path>     : Capture request
  - GET /capture/status  : View capture status
  - POST /capture/reset  : Clear all captures
 * Serving Flask app 'http_capture'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8000
 * Running on http://192.168.1.148:8000
Press CTRL+C to quit
 * Restarting with stat
Capture server starting. Events will be saved to: events/events-2025-10-22.json
Endpoints:
  - POST /<any-path>     : Capture request
  - GET /capture/status  : View capture status
  - POST /capture/reset  : Clear all captures
 * Debugger is active!
 * Debugger PIN: 453-309-063
[1] Captured POST to /event
127.0.0.1 - - [22/Oct/2025 17:19:45] "POST /event HTTP/1.1" 200 -
[2] Captured POST to /event
127.0.0.1 - - [22/Oct/2025 17:19:48] "POST /event HTTP/1.1" 200 -
[3] Captured POST to /event
127.0.0.1 - - [22/Oct/2025 17:19:52] "POST /event HTTP/1.1" 200 -
[4] Captured POST to /event
127.0.0.1 - - [22/Oct/2025 17:19:55] "POST /event HTTP/1.1" 200 -
[5] Captured POST to /event
127.0.0.1 - - [22/Oct/2025 17:19:57] "POST /event HTTP/1.1" 200 -
[6] Captured POST to /event
127.0.0.1 - - [22/Oct/2025 17:20:00] "POST /event HTTP/1.1" 200 -
[7] Captured POST to /event
127.0.0.1 - - [22/Oct/2025 17:20:03] "POST /event HTTP/1.1" 200 -
[8] Captured POST to /event
127.0.0.1 - - [22/Oct/2025 17:20:05] "POST /event HTTP/1.1" 200 -
[9] Captured POST to /event
127.0.0.1 - - [22/Oct/2025 17:20:08] "POST /event HTTP/1.1" 200 -
[10] Captured POST to /event
127.0.0.1 - - [22/Oct/2025 17:20:11] "POST /event HTTP/1.1" 200 -
[11] Captured POST to /event
127.0.0.1 - - [22/Oct/2025 17:20:14] "POST /event HTTP/1.1" 200 -
[12] Captured POST to /event
127.0.0.1 - - [22/Oct/2025 17:20:17] "POST /event HTTP/1.1" 200 -
^C%                                                                                                  
```