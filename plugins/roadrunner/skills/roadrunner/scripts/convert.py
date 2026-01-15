#!/usr/bin/env python3
"""
RoadRunner Coordinate Conversion Utilities

RoadRunner uses: origin at field CENTER, inches, radians
Pedro Pathing uses: origin at field CORNER, inches, radians
FTC/Limelight uses: origin at field CENTER, meters, degrees

Usage:
    python convert.py roadrunner-to-pedro <x_inches> <y_inches> <heading_radians>
    python convert.py pedro-to-roadrunner <x_inches> <y_inches> <heading_radians>
    python convert.py roadrunner-to-ftc <x_inches> <y_inches> <heading_radians>
    python convert.py ftc-to-roadrunner <x_meters> <y_meters> <heading_degrees>
    python convert.py mirror-blue <x_inches> <y_inches> <heading_radians>
    python convert.py all <x_inches> <y_inches> <heading_radians>

Examples:
    python convert.py roadrunner-to-pedro 0 0 0
    python convert.py pedro-to-roadrunner 72 72 0
    python convert.py ftc-to-roadrunner 0.5 1.2 90
    python convert.py mirror-blue 12 -62 1.57
    python convert.py all 12 -62 1.57
"""

import sys
import math

# Constants
FIELD_SIZE_INCHES = 144.0
FIELD_CENTER_INCHES = 72.0
TILE_SIZE_INCHES = 24.0
INCHES_PER_METER = 39.3701
METERS_PER_INCH = 0.0254


def roadrunner_to_pedro(rr_x: float, rr_y: float, heading_rad: float) -> tuple:
    """
    Convert RoadRunner coordinates to Pedro Pathing coordinates.

    RoadRunner: Origin at field center, inches, radians
    Pedro: Origin at field corner, inches, radians
    """
    pedro_x = rr_x + FIELD_CENTER_INCHES
    pedro_y = rr_y + FIELD_CENTER_INCHES
    return pedro_x, pedro_y, heading_rad


def pedro_to_roadrunner(pedro_x: float, pedro_y: float, heading_rad: float) -> tuple:
    """
    Convert Pedro Pathing coordinates to RoadRunner coordinates.

    Pedro: Origin at field corner, inches, radians
    RoadRunner: Origin at field center, inches, radians
    """
    rr_x = pedro_x - FIELD_CENTER_INCHES
    rr_y = pedro_y - FIELD_CENTER_INCHES
    return rr_x, rr_y, heading_rad


def roadrunner_to_ftc(rr_x: float, rr_y: float, heading_rad: float) -> tuple:
    """
    Convert RoadRunner coordinates to FTC/Limelight coordinates.

    RoadRunner: Origin at field center, inches, radians
    FTC: Origin at field center, meters, degrees
    """
    ftc_x = rr_x * METERS_PER_INCH
    ftc_y = rr_y * METERS_PER_INCH
    heading_deg = math.degrees(heading_rad)
    return ftc_x, ftc_y, heading_deg


def ftc_to_roadrunner(ftc_x: float, ftc_y: float, heading_deg: float) -> tuple:
    """
    Convert FTC/Limelight coordinates to RoadRunner coordinates.

    FTC: Origin at field center, meters, degrees
    RoadRunner: Origin at field center, inches, radians
    """
    rr_x = ftc_x * INCHES_PER_METER
    rr_y = ftc_y * INCHES_PER_METER
    heading_rad = math.radians(heading_deg)
    return rr_x, rr_y, heading_rad


def roadrunner_to_tile(rr_x: float, rr_y: float) -> tuple:
    """
    Convert RoadRunner coordinates to tile coordinates.
    Tile (0,0) is bottom-left corner, each tile is 24".
    """
    # First convert to Pedro (corner origin)
    pedro_x = rr_x + FIELD_CENTER_INCHES
    pedro_y = rr_y + FIELD_CENTER_INCHES
    # Then to tiles
    tile_x = pedro_x / TILE_SIZE_INCHES
    tile_y = pedro_y / TILE_SIZE_INCHES
    return tile_x, tile_y


def tile_to_roadrunner(tile_x: float, tile_y: float) -> tuple:
    """
    Convert tile coordinates to RoadRunner coordinates.
    Returns the corner of the tile in RoadRunner coordinates.
    """
    pedro_x = tile_x * TILE_SIZE_INCHES
    pedro_y = tile_y * TILE_SIZE_INCHES
    rr_x = pedro_x - FIELD_CENTER_INCHES
    rr_y = pedro_y - FIELD_CENTER_INCHES
    return rr_x, rr_y


def tile_center_to_roadrunner(tile_x: int, tile_y: int) -> tuple:
    """
    Get RoadRunner coordinates for the center of a tile.
    """
    pedro_x = (tile_x * TILE_SIZE_INCHES) + (TILE_SIZE_INCHES / 2)
    pedro_y = (tile_y * TILE_SIZE_INCHES) + (TILE_SIZE_INCHES / 2)
    rr_x = pedro_x - FIELD_CENTER_INCHES
    rr_y = pedro_y - FIELD_CENTER_INCHES
    return rr_x, rr_y


def mirror_for_blue(red_x: float, red_y: float, red_heading: float) -> tuple:
    """
    Mirror a red alliance RoadRunner pose for blue alliance.
    X is mirrored around center (which is 0 in RoadRunner), heading is flipped.
    """
    blue_x = -red_x
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
        return "Forward-Right"
    elif 67.5 < degrees <= 112.5:
        return "Forward (+Y)"
    elif 112.5 < degrees <= 157.5:
        return "Forward-Left"
    elif degrees > 157.5 or degrees < -157.5:
        return "Left (-X)"
    elif -157.5 <= degrees < -112.5:
        return "Back-Left"
    elif -112.5 <= degrees < -67.5:
        return "Back (-Y)"
    elif -67.5 <= degrees < -22.5:
        return "Back-Right"
    return "Unknown"


def print_usage():
    print(__doc__)


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        if command == "roadrunner-to-pedro":
            if len(sys.argv) != 5:
                print("Usage: roadrunner-to-pedro <x_inches> <y_inches> <heading_radians>")
                sys.exit(1)
            x, y, h = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
            px, py, ph = roadrunner_to_pedro(x, y, h)
            print(f"RoadRunner: ({x:.2f}\", {y:.2f}\") @ {h:.4f} rad ({math.degrees(h):.1f}°)")
            print(f"Pedro:      ({px:.2f}\", {py:.2f}\") @ {ph:.4f} rad ({math.degrees(ph):.1f}°)")
            print(f"Direction:  {heading_to_direction(h)}")
            tx, ty = roadrunner_to_tile(x, y)
            print(f"Tile:       ({tx:.2f}, {ty:.2f})")

        elif command == "pedro-to-roadrunner":
            if len(sys.argv) != 5:
                print("Usage: pedro-to-roadrunner <x_inches> <y_inches> <heading_radians>")
                sys.exit(1)
            x, y, h = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
            rx, ry, rh = pedro_to_roadrunner(x, y, h)
            print(f"Pedro:      ({x:.2f}\", {y:.2f}\") @ {h:.4f} rad")
            print(f"RoadRunner: ({rx:.2f}\", {ry:.2f}\") @ {rh:.4f} rad ({math.degrees(rh):.1f}°)")
            print(f"Direction:  {heading_to_direction(rh)}")

        elif command == "roadrunner-to-ftc":
            if len(sys.argv) != 5:
                print("Usage: roadrunner-to-ftc <x_inches> <y_inches> <heading_radians>")
                sys.exit(1)
            x, y, h = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
            fx, fy, fh = roadrunner_to_ftc(x, y, h)
            print(f"RoadRunner: ({x:.2f}\", {y:.2f}\") @ {h:.4f} rad")
            print(f"FTC:        ({fx:.3f}m, {fy:.3f}m) @ {fh:.1f}°")

        elif command == "ftc-to-roadrunner":
            if len(sys.argv) != 5:
                print("Usage: ftc-to-roadrunner <x_meters> <y_meters> <heading_degrees>")
                sys.exit(1)
            x, y, h = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
            rx, ry, rh = ftc_to_roadrunner(x, y, h)
            print(f"FTC:        ({x:.3f}m, {y:.3f}m) @ {h:.1f}°")
            print(f"RoadRunner: ({rx:.2f}\", {ry:.2f}\") @ {rh:.4f} rad ({math.degrees(rh):.1f}°)")
            print(f"Direction:  {heading_to_direction(rh)}")

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

        elif command == "tile-to-roadrunner":
            if len(sys.argv) != 4:
                print("Usage: tile-to-roadrunner <tile_x> <tile_y>")
                sys.exit(1)
            tx, ty = float(sys.argv[2]), float(sys.argv[3])
            rx, ry = tile_to_roadrunner(tx, ty)
            print(f"Tile:       ({tx:.2f}, {ty:.2f}) corner")
            print(f"RoadRunner: ({rx:.2f}\", {ry:.2f}\")")

        elif command == "tile-center":
            if len(sys.argv) != 4:
                print("Usage: tile-center <tile_x> <tile_y>")
                sys.exit(1)
            tx, ty = int(sys.argv[2]), int(sys.argv[3])
            rx, ry = tile_center_to_roadrunner(tx, ty)
            print(f"Tile:       ({tx}, {ty}) center")
            print(f"RoadRunner: ({rx:.2f}\", {ry:.2f}\")")

        elif command == "all":
            if len(sys.argv) != 5:
                print("Usage: all <x_inches> <y_inches> <heading_radians>")
                sys.exit(1)
            x, y, h = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])

            # RoadRunner (input)
            print(f"RoadRunner: ({x:.2f}\", {y:.2f}\") @ {h:.4f} rad ({math.degrees(h):.1f}°)")
            print(f"Direction:  {heading_to_direction(h)}")
            print()

            # Pedro
            px, py, ph = roadrunner_to_pedro(x, y, h)
            print(f"Pedro:      ({px:.2f}\", {py:.2f}\") @ {ph:.4f} rad")

            # FTC
            fx, fy, fh = roadrunner_to_ftc(x, y, h)
            print(f"FTC:        ({fx:.3f}m, {fy:.3f}m) @ {fh:.1f}°")

            # Tile
            tx, ty = roadrunner_to_tile(x, y)
            print(f"Tile:       ({tx:.2f}, {ty:.2f})")

            # Blue mirror
            bx, by, bh = mirror_for_blue(x, y, h)
            print(f"Blue mirror: ({bx:.2f}\", {by:.2f}\") @ {bh:.4f} rad ({math.degrees(bh):.1f}°)")

        else:
            print(f"Unknown command: {command}")
            print_usage()
            sys.exit(1)

    except ValueError as e:
        print(f"Error parsing arguments: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
