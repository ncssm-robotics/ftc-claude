#!/usr/bin/env python3
"""
DECODE Field Coordinate Conversion Utilities

Usage:
    python convert.py ftc-to-pedro <x_meters> <y_meters> <heading_degrees>
    python convert.py pedro-to-ftc <x_inches> <y_inches> <heading_radians>
    python convert.py tile-to-pedro <tile_x> <tile_y>
    python convert.py tile-center <tile_x> <tile_y>
    python convert.py mirror-blue <x_inches> <y_inches> <heading_radians>
    python convert.py all <x_inches> <y_inches>

Examples:
    python convert.py ftc-to-pedro 0 0 90
    python convert.py tile-to-pedro 3 3
    python convert.py mirror-blue 7 6.75 0
"""

import sys
import math

# Constants
FIELD_SIZE_INCHES = 144.0
FIELD_CENTER_INCHES = 72.0
TILE_SIZE_INCHES = 24.0
INCHES_PER_METER = 39.3701
METERS_PER_INCH = 0.0254


def ftc_to_pedro(ftc_x: float, ftc_y: float, heading_deg: float) -> tuple:
    """
    Convert FTC coordinates (meters, degrees) to Pedro (inches, radians).

    FTC: Origin at field center, meters
    Pedro: Origin at field corner, inches
    """
    pedro_x = (ftc_x * INCHES_PER_METER) + FIELD_CENTER_INCHES
    pedro_y = (ftc_y * INCHES_PER_METER) + FIELD_CENTER_INCHES
    heading_rad = math.radians(heading_deg)
    return pedro_x, pedro_y, heading_rad


def pedro_to_ftc(pedro_x: float, pedro_y: float, heading_rad: float) -> tuple:
    """
    Convert Pedro coordinates (inches, radians) to FTC (meters, degrees).
    """
    ftc_x = (pedro_x - FIELD_CENTER_INCHES) * METERS_PER_INCH
    ftc_y = (pedro_y - FIELD_CENTER_INCHES) * METERS_PER_INCH
    heading_deg = math.degrees(heading_rad)
    return ftc_x, ftc_y, heading_deg


def tile_to_pedro(tile_x: float, tile_y: float) -> tuple:
    """
    Convert tile coordinates to Pedro inches.
    Tile (0,0) is bottom-left corner of field.
    """
    pedro_x = tile_x * TILE_SIZE_INCHES
    pedro_y = tile_y * TILE_SIZE_INCHES
    return pedro_x, pedro_y


def tile_center_to_pedro(tile_x: int, tile_y: int) -> tuple:
    """
    Get Pedro coordinates for center of a tile.
    """
    pedro_x = (tile_x * TILE_SIZE_INCHES) + (TILE_SIZE_INCHES / 2)
    pedro_y = (tile_y * TILE_SIZE_INCHES) + (TILE_SIZE_INCHES / 2)
    return pedro_x, pedro_y


def pedro_to_tile(pedro_x: float, pedro_y: float) -> tuple:
    """
    Convert Pedro coordinates to tile coordinates.
    """
    tile_x = pedro_x / TILE_SIZE_INCHES
    tile_y = pedro_y / TILE_SIZE_INCHES
    return tile_x, tile_y


def mirror_for_blue(red_x: float, red_y: float, red_heading: float) -> tuple:
    """
    Mirror a red alliance pose for blue alliance.
    X is mirrored around center, heading is flipped.
    """
    blue_x = FIELD_SIZE_INCHES - red_x
    blue_y = red_y  # Y unchanged
    blue_heading = normalize_radians(math.pi - red_heading)
    return blue_x, blue_y, blue_heading


def normalize_radians(angle: float) -> float:
    """Normalize angle to [-PI, PI] radians."""
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle


def normalize_degrees(angle: float) -> float:
    """Normalize angle to [-180, 180] degrees."""
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    return angle


def heading_to_direction(radians: float) -> str:
    """Convert heading to human-readable direction."""
    degrees = math.degrees(normalize_radians(radians))
    if -22.5 <= degrees <= 22.5:
        return "Right (+X)"
    elif 22.5 < degrees <= 67.5:
        return "Right-Back"
    elif 67.5 < degrees <= 112.5:
        return "Back (+Y)"
    elif 112.5 < degrees <= 157.5:
        return "Left-Back"
    elif degrees > 157.5 or degrees < -157.5:
        return "Left (-X)"
    elif -157.5 <= degrees < -112.5:
        return "Left-Audience"
    elif -112.5 <= degrees < -67.5:
        return "Audience (-Y)"
    elif -67.5 <= degrees < -22.5:
        return "Right-Audience"
    return "Unknown"


def print_usage():
    print(__doc__)


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        if command == "ftc-to-pedro":
            if len(sys.argv) != 5:
                print("Usage: ftc-to-pedro <x_meters> <y_meters> <heading_degrees>")
                sys.exit(1)
            x, y, h = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
            px, py, ph = ftc_to_pedro(x, y, h)
            print(f"FTC:   ({x:.3f}m, {y:.3f}m) @ {h:.1f}°")
            print(f"Pedro: ({px:.2f}\", {py:.2f}\") @ {ph:.4f} rad ({math.degrees(ph):.1f}°)")
            print(f"Direction: {heading_to_direction(ph)}")
            tx, ty = pedro_to_tile(px, py)
            print(f"Tile:  ({tx:.2f}, {ty:.2f})")

        elif command == "pedro-to-ftc":
            if len(sys.argv) != 5:
                print("Usage: pedro-to-ftc <x_inches> <y_inches> <heading_radians>")
                sys.exit(1)
            x, y, h = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
            fx, fy, fh = pedro_to_ftc(x, y, h)
            print(f"Pedro: ({x:.2f}\", {y:.2f}\") @ {h:.4f} rad")
            print(f"FTC:   ({fx:.3f}m, {fy:.3f}m) @ {fh:.1f}°")
            tx, ty = pedro_to_tile(x, y)
            print(f"Tile:  ({tx:.2f}, {ty:.2f})")

        elif command == "tile-to-pedro":
            if len(sys.argv) != 4:
                print("Usage: tile-to-pedro <tile_x> <tile_y>")
                sys.exit(1)
            tx, ty = float(sys.argv[2]), float(sys.argv[3])
            px, py = tile_to_pedro(tx, ty)
            print(f"Tile:  ({tx:.2f}, {ty:.2f})")
            print(f"Pedro: ({px:.2f}\", {py:.2f}\")")

        elif command == "tile-center":
            if len(sys.argv) != 4:
                print("Usage: tile-center <tile_x> <tile_y>")
                sys.exit(1)
            tx, ty = int(sys.argv[2]), int(sys.argv[3])
            px, py = tile_center_to_pedro(tx, ty)
            print(f"Tile:  ({tx}, {ty}) center")
            print(f"Pedro: ({px:.2f}\", {py:.2f}\")")

        elif command == "mirror-blue":
            if len(sys.argv) != 5:
                print("Usage: mirror-blue <x_inches> <y_inches> <heading_radians>")
                sys.exit(1)
            rx, ry, rh = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
            bx, by, bh = mirror_for_blue(rx, ry, rh)
            print(f"Red:   ({rx:.2f}\", {ry:.2f}\") @ {rh:.4f} rad ({math.degrees(rh):.1f}°)")
            print(f"Blue:  ({bx:.2f}\", {by:.2f}\") @ {bh:.4f} rad ({math.degrees(bh):.1f}°)")
            print(f"Red direction:  {heading_to_direction(rh)}")
            print(f"Blue direction: {heading_to_direction(bh)}")

        elif command == "all":
            if len(sys.argv) != 4:
                print("Usage: all <x_inches> <y_inches>")
                sys.exit(1)
            px, py = float(sys.argv[2]), float(sys.argv[3])
            fx, fy, _ = pedro_to_ftc(px, py, 0)
            tx, ty = pedro_to_tile(px, py)
            bx, by, _ = mirror_for_blue(px, py, 0)
            print(f"Pedro: ({px:.2f}\", {py:.2f}\")")
            print(f"FTC:   ({fx:.3f}m, {fy:.3f}m)")
            print(f"Tile:  ({tx:.2f}, {ty:.2f})")
            print(f"Blue mirror: ({bx:.2f}\", {by:.2f}\")")

        else:
            print(f"Unknown command: {command}")
            print_usage()
            sys.exit(1)

    except ValueError as e:
        print(f"Error parsing arguments: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
