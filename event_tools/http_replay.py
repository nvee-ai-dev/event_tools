"""
Author: Martin

Date: 2025-09-23

License: Unlicense

Description:
    Replays a captured events file to a specified URL
"""

import requests
import json
import sys
import time
from datetime import datetime


def replay_sequence(
    capture_file="captured_requests.json",
    target_base_url="http://localhost:3001",
    speed_multiplier=1.0,
):
    """
    Replay all captured requests in sequence with original timing

    Args:
        capture_file: Path to captured requests JSON
        target_base_url: Base URL to replay requests to
        speed_multiplier: Speed up (>1.0) or slow down (<1.0) replay. Default 1.0 = real-time
    """

    # Load captured sequence
    with open(capture_file) as f:
        data = json.load(f)

    events = data["events"]

    if not events:
        print("No events to replay")
        return []

    print(
        f"Replaying {len(events)} events from session started at {data['session_start']}"
    )
    print(f"Target: {target_base_url}")
    print(f"Speed multiplier: {speed_multiplier}x")
    print(f"{'='*60}\n")

    # Parse timestamps
    event_times = []
    for event in events:
        event_time = datetime.fromisoformat(event["timestamp"])
        event_times.append(event_time)

    # Calculate delays relative to first event
    first_event_time = event_times[0]
    delays = []
    for event_time in event_times:
        delay = (event_time - first_event_time).total_seconds()
        delays.append(delay / speed_multiplier)  # Apply speed multiplier

    # Show timing preview
    print("Timing preview:")
    for i, (event, delay) in enumerate(zip(events, delays), 1):
        print(f"  [{i}] T+{delay:.3f}s: POST {event['path']}")
    print(f"\n{'='*60}\n")

    results = []
    replay_start = time.time()

    for i, (event, target_delay) in enumerate(zip(events, delays)):
        seq = event["sequence"]
        path = event["path"]
        url = f"{target_base_url}{path}"

        # Calculate how long to wait
        elapsed = time.time() - replay_start
        wait_time = target_delay - elapsed

        if wait_time > 0:
            print(f"[{seq}] Waiting {wait_time:.3f}s before replaying POST {path}...")
            time.sleep(wait_time)
        else:
            print(
                f"[{seq}] Replaying POST {path} (running {-wait_time:.3f}s behind schedule)..."
            )

        actual_time = time.time() - replay_start

        try:
            # Prepare headers (exclude host and content-length)
            headers = {
                k: v
                for k, v in event["headers"].items()
                if k.lower() not in ["host", "content-length", "content-type"]
            }

            request_start = time.time()

            # Make request
            if isinstance(event["body"], dict):
                # JSON body
                response = requests.post(
                    url, json=event["body"], headers=headers, timeout=10
                )
            else:
                # Text body
                headers["Content-Type"] = "text/plain"
                response = requests.post(
                    url, data=event["body"], headers=headers, timeout=10
                )

            request_duration = time.time() - request_start

            result = {
                "sequence": seq,
                "path": path,
                "status_code": response.status_code,
                "success": response.status_code < 400,
                "scheduled_time": target_delay,
                "actual_time": actual_time,
                "timing_drift": actual_time - target_delay,
                "request_duration": request_duration,
            }

            # Try to parse response as JSON
            try:
                result["response"] = response.json()
            except:
                result["response"] = response.text[:200]  # First 200 chars

            results.append(result)

            status_icon = "✓" if result["success"] else "✗"
            print(
                f"  {status_icon} Status: {response.status_code} "
                f"(took {request_duration:.3f}s, drift: {result['timing_drift']:+.3f}s)"
            )

        except Exception as e:
            actual_time = time.time() - replay_start
            print(f"  ✗ Error: {e}")
            results.append(
                {
                    "sequence": seq,
                    "path": path,
                    "error": str(e),
                    "success": False,
                    "scheduled_time": target_delay,
                    "actual_time": actual_time,
                    "timing_drift": actual_time - target_delay,
                }
            )

    total_duration = time.time() - replay_start

    # Summary
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total events: {len(results)}")
    print(f"  Successful: {sum(1 for r in results if r.get('success'))}")
    print(f"  Failed: {sum(1 for r in results if not r.get('success'))}")
    print(f"  Total duration: {total_duration:.3f}s")
    print(f"  Original duration: {delays[-1]:.3f}s")
    print(
        f"  Average timing drift: {sum(abs(r.get('timing_drift', 0)) for r in results) / len(results):.3f}s"
    )

    # Save results
    results_file = "replay_results.json"
    with open(results_file, "w") as f:
        json.dump(
            {
                "original_session": data["session_start"],
                "replay_timestamp": datetime.now().isoformat(),
                "target_url": target_base_url,
                "speed_multiplier": speed_multiplier,
                "total_duration": total_duration,
                "results": results,
            },
            f,
            indent=2,
        )

    print(f"\nResults saved to: {results_file}")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Replay captured HTTP requests, preserve relative timing"
    )
    parser.add_argument(
        "target_url",
        nargs="?",
        default="http://localhost:3000",
        help="Target base URL (default: http://localhost:3001)",
    )
    parser.add_argument(
        "-f",
        "--file",
        default="captured_requests.json",
        help="Capture file to replay (default: captured_requests.json)",
    )
    parser.add_argument(
        "-s",
        "--speed",
        type=float,
        default=1.0,
        help="Speed multiplier (default: 1.0 = real-time, 2.0 = 2x faster, 0.5 = half speed)",
    )

    args = parser.parse_args()

    replay_sequence(
        capture_file=args.file,
        target_base_url=args.target_url,
        speed_multiplier=args.speed,
    )

    sys.exit(0)
