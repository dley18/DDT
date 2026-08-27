"""Module that manages the core dictionary of selected user data."""

from datetime import datetime, timedelta

from typing import List, Dict
from config.point_mapping import VFD_POINTS
from util.time_util import convert_timestamp_to_readable


class SelectedDataManager:
    """Manages dictionary operations for the user selected data."""

    def __init__(self):

        self.data = {}
        self.data["io"] = {}
        self.data["vfd"] = {}
        self.data["preset"] = {}

    def add_point(self, name: str, time_value_list: List) -> bool:
        """
        Add a point to the data dictionary

        Parameters:
          name (str): Name of the IO or VFD Point
          time_value_list (List): List of timestamp and value entries for the point

        Returns:
          bool: True if adding successful, False otherwise
        """

        try:
            if name in VFD_POINTS.keys():
                self.data["vfd"][name] = time_value_list
            else:
                self.data["io"][name] = time_value_list
            return True
        except Exception as e:
            pass
            return False

    def add_preset(
        self, preset_name: str, point_name: str, time_value_list: List
    ) -> bool:
        """
        Add an preset graph to the data dictionary

        Parameters:
          preset_name (str): Name of the preset
          point_name (str): Name of the point to add
          time_value_list (List): List of timestamp and value entries for the preset

        Returns:
          bool: True if adding successful, False otherwise
        """
        try:
            # Create nested preset dictionary if not already created
            if preset_name not in self.data["preset"]:
                self.data["preset"][preset_name] = {}

            self.data["preset"][preset_name][point_name] = time_value_list
            return True
        except Exception as e:
            pass
            return False

    def get_data(self) -> Dict:
        """Get the data dictionary."""
        return self.data