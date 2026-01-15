#!/usr/bin/env python3
"""
Telemetry Recorder for Controller Tuning

Captures telemetry data during tuning runs using two methods:
1. Panels WebSocket (primary) - Real-time structured data
2. Logcat parsing (fallback) - Parses JSON from log messages

Output: JSON file with time-series data for analysis

Usage:
    uv run telemetry_recorder.py --duration 30 --output telemetry.json
    uv run telemetry_recorder.py --duration 30 --output telemetry.json --logcat-only
"""

# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "websocket-client",
# ]
# ///

import sys
import json
import time
import argparse
import subprocess
import threading
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import websocket
except ImportError:
    websocket = None


DEFAULT_HOST = "192.168.43.1"
DEFAULT_PORT = 8001
TIMEOUT = 5


class TelemetryRecorder:
    """Records telemetry from Panels WebSocket or logcat."""

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.url = f"ws://{host}:{port}/ws"
        self.ws: Optional[Any] = None
        self.data: List[Dict[str, Any]] = []
        self.recording = False
        self.start_time = 0.0

    def connect_websocket(self) -> bool:
        """Try to connect to Panels WebSocket."""
        if websocket is None:
            return False

        try:
            self.ws = websocket.create_connection(self.url, timeout=TIMEOUT)
            print(f"✓ Connected to Panels at {self.url}")
            return True
        except Exception as e:
            print(f"✗ Cannot connect to Panels: {e}")
            return False

    def record_from_websocket(self, duration: float) -> List[Dict[str, Any]]:
        """Record telemetry from Panels WebSocket."""
        if not self.connect_websocket():
            return []

        print(f"Recording telemetry for {duration} seconds via Panels WebSocket...")
        self.data = []
        self.start_time = time.time()
        end_time = self.start_time + duration

        try:
            while time.time() < end_time:
                try:
                    self.ws.settimeout(1.0)
                    message = self.ws.recv()
                    data = json.loads(message)

                    # Look for telemetry messages
                    if data.get("type") == "telemetry":
                        telemetry = data.get("data", {})
                        telemetry["timestamp"] = time.time() - self.start_time
                        self.data.append(telemetry)
                        print(f"  {len(self.data)} data points captured", end="\r")

                except websocket.WebSocketTimeoutException:
                    # Timeout is expected, continue recording
                    continue
                except Exception as e:
                    print(f"\nError receiving message: {e}")
                    break

        finally:
            if self.ws:
                self.ws.close()

        print(f"\n✓ Recorded {len(self.data)} data points from Panels")
        return self.data

    def record_from_logcat(self, duration: float) -> List[Dict[str, Any]]:
        """Record telemetry from logcat (fallback method)."""
        print(f"Recording telemetry for {duration} seconds via logcat...")
        self.data = []
        self.start_time = time.time()
        end_time = self.start_time + duration

        # Start logcat process
        try:
            # Filter for TUNING tag with JSON data
            process = subprocess.Popen(
                ["adb", "logcat", "-v", "brief", "-s", "TUNING:D"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            while time.time() < end_time:
                line = process.stdout.readline()
                if not line:
                    break

                # Parse logcat line format: "D/TUNING  ( 1234): {json data}"
                if "TUNING" in line and "{" in line:
                    try:
                        # Extract JSON part
                        json_start = line.index("{")
                        json_str = line[json_start:]
                        data = json.loads(json_str)

                        # Add relative timestamp if not present
                        if "t" not in data:
                            data["t"] = time.time() - self.start_time

                        self.data.append(data)
                        print(f"  {len(self.data)} data points captured", end="\r")

                    except (json.JSONDecodeError, ValueError) as e:
                        # Skip malformed JSON
                        continue

            process.terminate()
            process.wait(timeout=2)

        except FileNotFoundError:
            print("Error: adb not found. Is it installed and in PATH?")
            return []
        except Exception as e:
            print(f"Error running logcat: {e}")
            return []

        print(f"\n✓ Recorded {len(self.data)} data points from logcat")
        return self.data

    def record(self, duration: float, logcat_only: bool = False) -> List[Dict[str, Any]]:
        """
        Record telemetry with automatic fallback.

        Tries Panels WebSocket first (unless logcat_only=True),
        falls back to logcat if WebSocket fails.
        """
        if not logcat_only:
            data = self.record_from_websocket(duration)
            if data:
                return data

            print()
            print("Falling back to logcat telemetry capture...")
            print()

        return self.record_from_logcat(duration)

    def save(self, output_file: Path):
        """Save recorded data to JSON file."""
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump({
                "duration": time.time() - self.start_time if self.start_time else 0,
                "num_samples": len(self.data),
                "data": self.data
            }, f, indent=2)

        print(f"✓ Saved telemetry to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Record telemetry data for controller tuning"
    )
    parser.add_argument(
        "--duration", type=float, default=30.0,
        help="Recording duration in seconds (default: 30)"
    )
    parser.add_argument(
        "--output", type=str, required=True,
        help="Output JSON file path"
    )
    parser.add_argument(
        "--host", default=DEFAULT_HOST,
        help=f"Robot IP address (default: {DEFAULT_HOST})"
    )
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT,
        help=f"Panels port (default: {DEFAULT_PORT})"
    )
    parser.add_argument(
        "--logcat-only", action="store_true",
        help="Skip Panels WebSocket, use logcat only"
    )

    args = parser.parse_args()

    # Create recorder
    recorder = TelemetryRecorder(args.host, args.port)

    # Record telemetry
    data = recorder.record(args.duration, logcat_only=args.logcat_only)

    if not data:
        print("\nError: No telemetry data captured")
        print("Troubleshooting:")
        print("  - Is the OpMode running?")
        print("  - Is telemetry being logged to logcat (tag: TUNING)?")
        print("  - For Panels: Are you on robot WiFi?")
        return 1

    # Save to file
    output_path = Path(args.output)
    recorder.save(output_path)

    # Display summary
    print()
    print("Summary:")
    print(f"  Duration: {recorder.data[-1].get('t', 0):.1f} seconds")
    print(f"  Samples: {len(data)}")
    print(f"  Sample rate: {len(data) / (recorder.data[-1].get('t', 1) or 1):.1f} Hz")

    # Display sample data point
    if data:
        print()
        print("Sample data point:")
        print(json.dumps(data[0], indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
