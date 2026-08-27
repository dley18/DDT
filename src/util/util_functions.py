"Shared Utility Functions Module"

from typing import List, Dict
from config.ui_config import SEARCH_TYPE_MAP
from data.database_manager import DatabaseManager

def flip_bits(time_value: List[Dict[str, int]]) -> None:
    """
    Modifies time_value list in place and flips all of the value bits using XOR

    Params:
        time_value (List[Dict[str, int]]): Original time_value dict with bits
    """
    for entry in time_value:
        entry["value"] = entry["value"] ^ 1


def convert_io_type(io_type: str):
    """Converts an io type like AI to the table AnalogInput or AnalogInput@0"""
    version = DatabaseManager.get_database_version()

    return SEARCH_TYPE_MAP[io_type][0] if version == "1" else SEARCH_TYPE_MAP[io_type][1]

