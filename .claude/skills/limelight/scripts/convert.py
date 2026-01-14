#!/usr/bin/env python3
"""
Limelight Coordinate Conversion Utilities

Usage:
    python convert.py botpose-to-pedro <x_meters> <y_meters> <yaw_degrees>
    python convert.py tx-to-turret <tx_degrees> [ticks_per_degree]
    python convert.py distance <ty_degrees> <camera_height_in> <camera_angle_deg> <target_height_in>

Examples:
    python convert.py botpose-to-pedro 0.5 1.2 45
    python convert.py tx-to-turret -5.5
    python convert.py tx-to-turret -5.5 12.0
    python convert.py distance 15 12 20 36
"""

import sys
import math

# Constants
FIELD_SIZE_INCHES = 144.0
FIELD_CENTER_INCHES = 72.0
INCHES_PER_METER = 39.3701
METERS_PER_INCH = 0.0254
DEFAULT_TICKS_PER_DEGREE = 10.0


def botpose_to_pedro(x_meters: float, y_meters: float, yaw_degrees: float) -> tuple:
    """
    Convert Limelight botpose (FTC coordinates) to Pedro Pathing pose.

    FTC: Origin at field center, meters, heading in degrees
    Pedro: Origin at field corner, inches, heading in radians
    """
    pedro_x = (x_meters * INCHES_PER_METER) + FIELD_CENTER_INCHES
    pedro_y = (y_meters * INCHES_PER_METER) + FIELD_CENTER_INCHES
    heading_rad = math.radians(yaw_degrees)
    return pedro_x, pedro_y, heading_rad


def pedro_to_ftc(pedro_x: float, pedro_y: float, heading_rad: float) -> tuple:
    """
    Convert Pedro coordinates to FTC/Limelight coordinates.
    """
    ftc_x = (pedro_x - FIELD_CENTER_INCHES) * METERS_PER_INCH
    ftc_y = (pedro_y - FIELD_CENTER_INCHES) * METERS_PER_INCH
    heading_deg = math.degrees(heading_rad)
    return ftc_x, ftc_y, heading_deg


def tx_to_turret_ticks(tx_degrees: float, ticks_per_degree: float = DEFAULT_TICKS_PER_DEGREE) -> int:
    """
    Convert Limelight tx (degrees) to turret encoder ticks.

    tx positive = target to the left = rotate turret left (positive ticks)
    """
    return int(tx_degrees * ticks_per_degree)


def calculate_distance(ty_degrees: float, camera_height_in: float,
                       camera_angle_deg: float, target_height_in: float) -> float:
    """
    Calculate distance to target using ty and known heights.

    Uses: distance = (targetHeight - cameraHeight) / tan(cameraAngle + ty)
    """
    angle_rad = math.radians(camera_angle_deg + ty_degrees)
    if abs(math.tan(angle_rad)) < 0.001:
        return float('inf')
    return (target_height_in - camera_height_in) / math.tan(angle_rad)


def normalize_radians(angle: float) -> float:
    """Normalize angle to [-PI, PI] radians."""
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
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
        if command == "botpose-to-pedro":
            if len(sys.argv) != 5:
                print("Usage: botpose-to-pedro <x_meters> <y_meters> <yaw_degrees>")
                sys.exit(1)
            x, y, yaw = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
            px, py, ph = botpose_to_pedro(x, y, yaw)
            print(f"Limelight botpose: ({x:.3f}m, {y:.3f}m) @ {yaw:.1f}°")
            print(f"Pedro:             ({px:.2f}\", {py:.2f}\") @ {ph:.4f} rad")
            print(f"Direction:         {heading_to_direction(ph)}")

        elif command == "tx-to-turret":
            if len(sys.argv) < 3:
                print("Usage: tx-to-turret <tx_degrees> [ticks_per_degree]")
                sys.exit(1)
            tx = float(sys.argv[2])
            tpd = float(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_TICKS_PER_DEGREE
            ticks = tx_to_turret_ticks(tx, tpd)
            direction = "LEFT" if tx > 0 else "RIGHT" if tx < 0 else "CENTER"
            print(f"tx:              {tx:.2f}° ({direction})")
            print(f"Ticks/degree:    {tpd:.1f}")
            print(f"Turret ticks:    {ticks}")

        elif command == "distance":
            if len(sys.argv) != 6:
                print("Usage: distance <ty_degrees> <camera_height_in> <camera_angle_deg> <target_height_in>")
                sys.exit(1)
            ty = float(sys.argv[2])
            cam_h = float(sys.argv[3])
            cam_angle = float(sys.argv[4])
            target_h = float(sys.argv[5])
            dist = calculate_distance(ty, cam_h, cam_angle, target_h)
            print(f"ty:            {ty:.2f}°")
            print(f"Camera height: {cam_h:.1f}\"")
            print(f"Camera angle:  {cam_angle:.1f}°")
            print(f"Target height: {target_h:.1f}\"")
            print(f"Distance:      {dist:.2f}\"")

        else:
            print(f"Unknown command: {command}")
            print_usage()
            sys.exit(1)

    except ValueError as e:
        print(f"Error parsing arguments: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
