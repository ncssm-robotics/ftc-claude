#!/usr/bin/env python3
"""
Panels Configurables Updater

Updates @Configurable parameters via Panels WebSocket in real-time.
Uses the same PanelsClient pattern as panels_client.py.

Usage:
    uv run config_updater.py get                          # List all configurables
    uv run config_updater.py set KEY VALUE               # Set single configurable
    uv run config_updater.py batch config.json           # Batch update from JSON

Example config.json:
    {
        "ELEVATOR_KP": 0.005,
        "ELEVATOR_KD": 0.0002,
        "ELEVATOR_KG": 0.15
    }
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
from typing import Optional, Dict, Any

try:
    import websocket
except ImportError:
    print("Error: websocket-client not installed")
    print("Run with: uv run config_updater.py <command>")
    sys.exit(1)


DEFAULT_HOST = "192.168.43.1"
DEFAULT_PORT = 8001
TIMEOUT = 5


class ConfigUpdater:
    """WebSocket client for updating Panels configurables."""

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.url = f"ws://{host}:{port}/ws"
        self.ws: Optional[websocket.WebSocket] = None
        self.configurables: Dict[str, Any] = {}

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

    def get_configurables(self) -> Dict[str, Any]:
        """Get all available configurables."""
        if not self.connect():
            return {}

        # Request configurables list
        self.send_message("requestConfigurables", None)

        # Wait for response
        response = self.receive_until("configurablesList", timeout=3)

        if response and "data" in response:
            self.configurables = response["data"].get("configurables", {})
            return self.configurables

        return {}

    def set_configurable(self, key: str, value: Any) -> bool:
        """Set a single configurable value."""
        if not self.connect():
            return False

        # Send update message
        self.send_message("updateConfigurable", {
            "key": key,
            "value": value
        })

        # Wait for confirmation
        response = self.receive_until("configurableUpdated", timeout=2)

        if response and "data" in response:
            return response["data"].get("success", False)

        return False

    def batch_update(self, updates: Dict[str, Any]) -> Dict[str, bool]:
        """Update multiple configurables."""
        results = {}

        for key, value in updates.items():
            success = self.set_configurable(key, value)
            results[key] = success

            if success:
                print(f"✓ Updated {key} = {value}")
            else:
                print(f"✗ Failed to update {key}")

        return results


def cmd_get(args):
    """List all available configurables."""
    updater = ConfigUpdater(args.host, args.port)
    configurables = updater.get_configurables()
    updater.disconnect()

    if not configurables:
        print("No configurables found or cannot connect to Panels.")
        print()
        print("Troubleshooting:")
        print("  - Ensure an OpMode with @Config is running")
        print("  - Check that Panels dashboard is accessible")
        return 1

    print("Available Configurables")
    print("─" * 60)
    print()

    # Group by class
    by_class: Dict[str, Dict[str, Any]] = {}
    for key, value in configurables.items():
        # Extract class name (e.g., "TuningConfig.ELEVATOR_KP" -> "TuningConfig")
        parts = key.split(".")
        if len(parts) > 1:
            class_name = parts[0]
            field_name = ".".join(parts[1:])
        else:
            class_name = "Global"
            field_name = key

        if class_name not in by_class:
            by_class[class_name] = {}
        by_class[class_name][field_name] = value

    # Display grouped
    for class_name, fields in sorted(by_class.items()):
        print(f"{class_name}:")
        for field_name, value in sorted(fields.items()):
            type_name = type(value).__name__
            print(f"  {field_name:30} = {value:12} ({type_name})")
        print()

    return 0


def cmd_set(args):
    """Set a single configurable."""
    if not args.key or args.value is None:
        print("Error: Both KEY and VALUE required")
        print("Usage: config_updater.py set KEY VALUE")
        return 1

    updater = ConfigUpdater(args.host, args.port)

    # Try to parse value as number, fallback to string
    try:
        value = json.loads(args.value)
    except json.JSONDecodeError:
        value = args.value

    success = updater.set_configurable(args.key, value)
    updater.disconnect()

    if success:
        print(f"✓ Updated {args.key} = {value}")
        return 0
    else:
        print(f"✗ Failed to update {args.key}")
        print()
        print("Check:")
        print("  - Is the configurable name correct? Run 'get' to list all")
        print("  - Is an OpMode running?")
        print("  - Is the value the correct type (number, string, boolean)?")
        return 1


def cmd_batch(args):
    """Batch update configurables from JSON file."""
    if not args.file:
        print("Error: JSON file required")
        print("Usage: config_updater.py batch config.json")
        return 1

    try:
        with open(args.file) as f:
            updates = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.file}")
        print(f"  {e}")
        return 1

    if not isinstance(updates, dict):
        print("Error: JSON file must contain an object/dictionary")
        return 1

    updater = ConfigUpdater(args.host, args.port)
    results = updater.batch_update(updates)
    updater.disconnect()

    # Summary
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    print()
    print(f"Updated {success_count}/{total_count} configurables")

    if success_count < total_count:
        print()
        print("Failed updates:")
        for key, success in results.items():
            if not success:
                print(f"  - {key}")

    return 0 if success_count == total_count else 1


def main():
    parser = argparse.ArgumentParser(
        description="Panels Configurables Updater - Update @Config parameters in real-time"
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

    # get command
    get_parser = subparsers.add_parser("get", help="List all configurables")
    get_parser.set_defaults(func=cmd_get)

    # set command
    set_parser = subparsers.add_parser("set", help="Set a single configurable")
    set_parser.add_argument("key", nargs="?", help="Configurable key (e.g., TuningConfig.ELEVATOR_KP)")
    set_parser.add_argument("value", nargs="?", help="New value")
    set_parser.set_defaults(func=cmd_set)

    # batch command
    batch_parser = subparsers.add_parser("batch", help="Batch update from JSON file")
    batch_parser.add_argument("file", nargs="?", help="JSON file with key-value pairs")
    batch_parser.set_defaults(func=cmd_batch)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
