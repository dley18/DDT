"""CSV file generator module."""

import csv
import os
from typing import List, Dict, Any, Optional
from collections import defaultdict

from config.constants import DATA_FOLDER_PATH
from util.time_util import convert_timestamp_to_readable
from util.file_util import get_unique_filename


class CSVGenerator:
    """Manages CSV file creation and operations."""

    def __init__(self):
        self.csv_file_path = None
        self.headers = None

    def create_csv(self, csv_title: Optional[str], headers: List) -> bool:
        """
        Create a new CSV file with headers.

        Parameters: 
            csv_title Optional[str]: Title of CSV File
            headers List: List of CSV Headers

        Returns:
          bool: True if generation successful, False otherwise
        """
        try:
            # Get unique file name if file name already exists
            csv_title = get_unique_filename(os.path.join(DATA_FOLDER_PATH, csv_title))

            self.csv_file_path = os.path.join(DATA_FOLDER_PATH, csv_title)
            self.headers = headers

            with open(self.csv_file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.headers)
                writer.writeheader()

            return True
        except Exception as e:
            pass
            return False

    def write_to_csv(self, data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """
        Add csv data for preset graphs.

        Parameters:
            data (Dict[str, List[Dict[str, Any]]]): Dict containing point names and timestamp value list

        Returns:
            bool: True if successful, False otherwise
        """

        try: 
            timestamp_rows = defaultdict(dict)
            
            # For each point in the preset
            for point_name, time_value_list in data.items():
                # For each entry for this point
                for entry in time_value_list:
                    timestamp = entry["timestamp"]
                    timestamp_rows[timestamp][point_name] = entry["value"]

            # Sort timestamps
            sorted_timestamps = sorted(timestamp_rows)

            # Write to csv
            with open(self.csv_file_path, "a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.headers)
                
                for timestamp in sorted_timestamps:
                    row = {"Timestamp": convert_timestamp_to_readable(timestamp)}
                    row.update(timestamp_rows[timestamp])
                    writer.writerow(row)
            
            return True
        
        except Exception as e:
            pass
            return False