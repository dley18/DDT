"""Datetime operations module"""

from datetime import datetime, timedelta
from typing import Dict, List


def convert_timestamp_to_readable(timestamp: int):
    """Convert a timestamp (in nanoseconds) to a readable time."""

    # Convert nanoseconds to seconds
    timestamp_seconds = timestamp / 1_000_000_000
    return datetime.fromtimestamp(timestamp_seconds).strftime("%Y-%m-%d %H:%M:%S")


def get_unique_timestamps(plot_data: dict) -> set:
    """Get all unique timestamps from all points on a plot."""
    all_timestamps = set()
    for time_value_list in plot_data.values():
        for entry in time_value_list:
            all_timestamps.add(entry["timestamp"])

    # Sort for consistent x-axis
    return sorted(all_timestamps)


def enter_time_zone_offset(data: Dict, time_zone_offset: int) -> Dict:
    """
    Add or subtract time zone offset from all selected data timestamps.

    Parameters:
        data (Dict): Data dictionary to manipulate.
        time_zone_offset (int): Offset to apply to all timestamps (hours).
    """
    hours = time_zone_offset / 100
    offset = hours * 60 * 60 * 1_000_000_000

    for category in ["io", "vfd"]:
        for point_name, time_value_list in data[category].items():
            for entry in time_value_list:
                original_timestamp = int(float(entry["timestamp"]))
                adjusted_timestamp = original_timestamp + offset
                entry["timestamp"] = adjusted_timestamp

    for preset_name, preset_data in data["preset"].items():
        for point_name, time_value_list in preset_data.items():
            for entry in time_value_list:
                original_timestamp = int(float(entry["timestamp"]))
                adjusted_timestamp = original_timestamp + offset
                entry["timestamp"] = adjusted_timestamp

    return data


def apply_time_zone_offset_to_incidents(
    incidents: List[Dict], offset: int
) -> List[Dict]:
    """
    Apply time zone offset to incidents.

    Parameters:
        incidents (List[Dict]): List of all incidents
        offset (int): Time zone offset to apply

    Returns:
        List[Dict]: All incidents with offset applied
    """

    hours = offset / 100

    for entry in incidents:
        entry["timestamp"] = datetime.strptime(
            entry["timestamp"], "%Y-%m-%d %H:%M:%S"
        ) + timedelta(hours=hours)

    return incidents


def apply_time_zone_offset_to_report(timestamps: List, offset: int) -> List:
    """
    Apply time zone offest to report.

    Parameters:
        Timestamps (List): Starting and ending timestamps.

    Returns:
        tuple: New Starting time, new ending time.
    """

    hours = offset / 100

    new_timestamps = []

    for timestamp in timestamps:
        timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") + timedelta(
            hours=hours
        )
        new_timestamps.append(timestamp)

    return new_timestamps

def find_min_max_time(data: Dict) -> tuple:
    """
    Given the data dictionary, find the min and max time intervals.

    Parameters:
        data (dict): Data Dictionary

    Returns:
        tuple: (min_time, max_time)
    """

    min_time = None
    max_time = None

    for point_data in data.values():

        for entry in point_data:

            if min_time is None and max_time is None:
                min_time = entry["timestamp"]
                max_time = entry["timestamp"]

            if entry["timestamp"] > max_time:
                max_time = entry["timestamp"]
            elif entry["timestamp"] < min_time:
                min_time = entry["timestamp"]
            else:
                pass
    return convert_timestamp_to_readable(min_time), convert_timestamp_to_readable(max_time)
