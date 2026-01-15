#!/usr/bin/env python3
"""
Panels WebSocket Client for FTC Robot Control

Usage:
    uv run panels_client.py list                    # List OpModes
    uv run panels_client.py init "TeleOp Main"     # Initialize OpMode
    uv run panels_client.py start                   # Start OpMode
    uv run panels_client.py stop                    # Stop OpMode
    uv run panels_client.py status                  # Get current status

Requirements (handled by uv):
    websocket-client
"""

# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "websocket-client",
# ]
# ///

import sys
import json
import argparse
from typing import Optional, Any

try:
    import websocket
except ImportError:
    print("Error: websocket-client not installed")
    print("Run with: uv run panels_client.py <command>")
    sys.exit(1)


DEFAULT_HOST = "192.168.43.1"
DEFAULT_PORT = 8001
TIMEOUT = 5


class PanelsClient:
    """WebSocket client for Panels dashboard."""

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.url = f"ws://{host}:{port}/ws"
        self.ws: Optional[websocket.WebSocket] = None
        self.opmodes: list = []
        self.active_opmode: Optional[dict] = None

    def connect(self) -> bool:
        """Establish websocket connection."""
        try:
            self.ws = websocket.create_connection(self.url, timeout=TIMEOUT)
            return True
        except Exception as e:
            print(f"Error: Cannot connect to Panels at {self.url}")
            print(f"  {e}")
            print()
            print("Troubleshooting:")
            print("  1. Is the robot powered on?")
            print("  2. Are you on the robot's WiFi network?")
            print("  3. Is Panels installed and running?")
            return False

    def disconnect(self):
        """Close websocket connection."""
        if self.ws:
            self.ws.close()
            self.ws = None

    def send_message(self, msg_type: str, data: Any = None) -> Optional[dict]:
        """Send a message and wait for response."""
        if not self.ws:
            if not self.connect():
                return None

        message = json.dumps({"type": msg_type, "data": data})
        try:
            self.ws.send(message)
            # Wait for response
            response = self.ws.recv()
            return json.loads(response)
        except Exception as e:
            print(f"Error sending message: {e}")
            return None

    def receive_until(self, msg_type: str, timeout: float = TIMEOUT) -> Optional[dict]:
        """Receive messages until we get the expected type."""
        if not self.ws:
            if not self.connect():
                return None

        self.ws.settimeout(timeout)
        try:
            while True:
                response = self.ws.recv()
                data = json.loads(response)
                if data.get("type") == msg_type:
                    return data
        except websocket.WebSocketTimeoutException:
            return None
        except Exception as e:
            print(f"Error receiving: {e}")
            return None

    def list_opmodes(self) -> list:
        """Get list of available OpModes."""
        if not self.connect():
            return []

        # Request opmode list
        self.send_message("requestOpModes", None)

        # Wait for opModesList response
        response = self.receive_until("opModesList", timeout=3)

        if response and "data" in response:
            self.opmodes = response["data"].get("opModes", [])
            return self.opmodes

        return []

    def get_status(self) -> Optional[dict]:
        """Get current OpMode status."""
        if not self.connect():
            return None

        # Wait for activeOpMode message
        response = self.receive_until("activeOpMode", timeout=2)

        if response and "data" in response:
            self.active_opmode = response["data"]
            return self.active_opmode

        return None

    def init_opmode(self, name: str) -> bool:
        """Initialize an OpMode by name."""
        if not self.connect():
            return False

        self.send_message("initOpMode", name)

        # Wait for confirmation
        response = self.receive_until("activeOpMode", timeout=3)

        if response and "data" in response:
            status = response["data"].get("status", "")
            return status in ["INIT", "INITIALIZING"]

        return False

    def start_opmode(self) -> bool:
        """Start the currently initialized OpMode."""
        if not self.connect():
            return False

        self.send_message("startActiveOpMode", None)

        # Wait for confirmation
        response = self.receive_until("activeOpMode", timeout=3)

        if response and "data" in response:
            status = response["data"].get("status", "")
            return status in ["RUNNING", "STARTING"]

        return False

    def stop_opmode(self) -> bool:
        """Stop the currently running OpMode."""
        if not self.connect():
            return False

        self.send_message("stopActiveOpMode", None)

        # Wait for confirmation
        response = self.receive_until("activeOpMode", timeout=3)

        if response and "data" in response:
            status = response["data"].get("status", "")
            return status in ["STOPPED", "STOPPING", "STOP"]

        return False


def format_opmode(opmode: dict, index: int = 0) -> str:
    """Format an OpMode for display."""
    name = opmode.get("name", "Unknown")
    flavour = opmode.get("flavour", "TELEOP")
    group = opmode.get("group", "")

    icon = "🅰️ " if flavour == "AUTONOMOUS" else "🎮"
    group_str = f" ({group})" if group and group != "default" else ""

    if index > 0:
        return f"  {index}. {icon} {name}{group_str}"
    return f"{icon} {name}{group_str}"


def cmd_list(args):
    """List available OpModes."""
    client = PanelsClient(args.host, args.port)
    opmodes = client.list_opmodes()
    client.disconnect()

    if not opmodes:
        print("No OpModes found or cannot connect to Panels.")
        return 1

    # Separate by type
    auto = [op for op in opmodes if op.get("flavour") == "AUTONOMOUS"]
    teleop = [op for op in opmodes if op.get("flavour") == "TELEOP"]

    print("Available OpModes")
    print("─" * 40)

    idx = 1
    if auto:
        print("\nAutonomous:")
        for op in auto:
            print(format_opmode(op, idx))
            idx += 1

    if teleop:
        print("\nTeleOp:")
        for op in teleop:
            print(format_opmode(op, idx))
            idx += 1

    print()
    return 0


def cmd_status(args):
    """Get current status."""
    client = PanelsClient(args.host, args.port)
    status = client.get_status()
    client.disconnect()

    if not status:
        print("Cannot get status or no active OpMode.")
        return 1

    opmode = status.get("opMode", {})
    state = status.get("status", "UNKNOWN")
    name = opmode.get("name", "None") if opmode else "None"

    print(f"OpMode: {name}")
    print(f"Status: [{state}]")

    if status.get("startTimestamp"):
        print(f"Started: {status['startTimestamp']}")

    return 0


def cmd_init(args):
    """Initialize an OpMode."""
    if not args.name:
        print("Error: OpMode name required")
        print("Usage: panels_client.py init \"OpMode Name\"")
        return 1

    client = PanelsClient(args.host, args.port)
    success = client.init_opmode(args.name)
    client.disconnect()

    if success:
        print(f"✓ Initialized: {args.name}")
        print(f"  Status: [INIT]")
        print()
        print("Next: Run 'start' to begin")
        return 0
    else:
        print(f"✗ Failed to initialize: {args.name}")
        print()
        print("Check:")
        print("  - Is the OpMode name correct?")
        print("  - Run 'list' to see available OpModes")
        return 1


def cmd_start(args):
    """Start the initialized OpMode."""
    client = PanelsClient(args.host, args.port)
    success = client.start_opmode()
    client.disconnect()

    if success:
        print("✓ OpMode started")
        print("  Status: [RUNNING]")
        return 0
    else:
        print("✗ Failed to start OpMode")
        print()
        print("Check:")
        print("  - Is an OpMode initialized? Run 'init' first")
        print("  - Is the robot ready?")
        return 1


def cmd_stop(args):
    """Stop the running OpMode."""
    client = PanelsClient(args.host, args.port)
    success = client.stop_opmode()
    client.disconnect()

    if success:
        print("✓ OpMode stopped")
        print("  Status: [STOPPED]")
        return 0
    else:
        print("✗ Failed to stop OpMode")
        print()
        print("Check:")
        print("  - Is an OpMode running?")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Panels WebSocket Client for FTC Robot Control"
    )
    parser.add_argument(
        "--host", default=DEFAULT_HOST,
        help=f"Robot IP address (default: {DEFAULT_HOST})"
    )
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT,
        help=f"Panels port (default: {DEFAULT_PORT})"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # list command
    list_parser = subparsers.add_parser("list", help="List available OpModes")
    list_parser.set_defaults(func=cmd_list)

    # status command
    status_parser = subparsers.add_parser("status", help="Get current status")
    status_parser.set_defaults(func=cmd_status)

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize an OpMode")
    init_parser.add_argument("name", nargs="?", help="OpMode name")
    init_parser.set_defaults(func=cmd_init)

    # start command
    start_parser = subparsers.add_parser("start", help="Start initialized OpMode")
    start_parser.set_defaults(func=cmd_start)

    # stop command
    stop_parser = subparsers.add_parser("stop", help="Stop running OpMode")
    stop_parser.set_defaults(func=cmd_stop)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
