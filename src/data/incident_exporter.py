import csv
import os
from typing import Dict


from config.constants import DATA_FOLDER_PATH, ALARM_CSV_TITLE, ALARM_CSV_HEADERS

class IncidentExorter:
    """Handles exporting alarm log to a csv file."""

    def __init__(self, incidents: Dict):

        self.incidents = incidents
        self.csv_file_path = None

    def create_csv(self) -> bool:
        """
        Create a new CSV file with headers.

        Returns:
            bool: True if generation successful, False otherwise.
        """
        try:
            self.csv_file_path = os.path.join(DATA_FOLDER_PATH, ALARM_CSV_TITLE)

            with open(self.csv_file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=ALARM_CSV_HEADERS)
                writer.writeheader()

            return True
        except Exception as e:
            pass
            return False
        
    def export_to_csv(self) -> bool:
        """
        Export incidents to csv file.
        
        Returns:
            bool: True if export successful, False otherwise.
        """

        rows = []

        try:
            for entry in self.incidents:
                row = {
                    "Time": entry["timestamp"],
                    "Alarm": entry["text"],
                    "Label Color": entry["label_color"],
                    "Text Color": entry["text_color"],

                }
                rows.append(row)
            
            with open(self.csv_file_path, "a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=ALARM_CSV_HEADERS)
                writer.writerows(rows)
            
            return True

        except Exception as e:
            pass
            return False