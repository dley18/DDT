"""Main application workflow and logic."""

import os
from typing import List, Dict, Optional, Any
import threading

from config.point_mapping import VFD_POINTS, GRAPH_PRESETS
from config.constants import DATA_FOLDER_PATH, ALARM_CSV_TITLE
from data.database_manager import DatabaseManager
from data.selected_data_manager import SelectedDataManager
from data.incident_manager import IncidentManager
from data.csv_generator import CSVGenerator
from data.incident_exporter import IncidentExorter
from ui.components.search import Search
from util.file_util import (
    decompress_datadownload,
    merge_database_files,
    get_database_filepaths,
    open_file,
    get_lz4_database_version
)
from util.time_util import (
    convert_timestamp_to_readable,
    enter_time_zone_offset,
    apply_time_zone_offset_to_incidents,
    apply_time_zone_offset_to_report,
)
from util.util_functions import (
    convert_io_type,
    flip_bits
)
from viz.graph_generator import GraphGenerator


class WorkflowManager:
    """Manages the main data processing workflow."""

    def __init__(self, database_manager: Optional[DatabaseManager]):

        if database_manager:
            self.database_manager = database_manager

        self.time_zone_offset = None
        self.timezone_ready = threading.Event()

        self.incidents_for_export = None

    def load_files(self, file_paths: list) -> str:
        """
        Load and parse database files.

        Parameters:
            file_paths (list): Selected files

        Returns:
            str: Merged database file path or ""
        """

        # Get Database Version Number
        db_version_number = get_lz4_database_version(file_paths)
        DatabaseManager.set_database_version(db_version_number)

        # Decompress files
        decompress_datadownload(file_paths)

        # Merge files
        success = merge_database_files(get_database_filepaths())

        if success:
            self.pull_io_points()
            return os.path.join(DATA_FOLDER_PATH, "merged_db.sqlite")
        else:
            return ""

    def pull_io_points(self) -> List[Dict[str, Any]]:
        """
        Pulls all IO Points from the database to populate the 'Search Database'
        panel.

        Retuns:
            List[Dict[str, Any]]: List of all io points
        """ 
        points = self.database_manager.get_all_io_points()
        return points

    def process_data(
        self, io_points: List[Dict[str, Any]], vfd_points: List[Dict[str, Any]], graph_presets: list
    ) -> dict:
        """Query for selected points from the database file."""

        # Dictionary that holds each user selection and their corresponding data
        # ( ex. io: {}, vfd : {}, preset : {})
        selected_data_manager = SelectedDataManager()

        # User selected IO Points
        if io_points:
            try:

                io_point_info = (
                    {}
                )  # io_point: {ioid: "", iotype: "", ioname: "", active: ""}

                # Get IO Point info
                for io_point in io_points:
                    name = io_point["name"]
                    io_type = io_point["type"]


                    # Retrieve data from IOConfig@0
                    io_point_info[name] = self.database_manager.get_io_point_info(
                        name,
                        io_type
                    )

                    if io_point_info[name]["active"] == 0:
                        print(f"DEBUG: {io_point} was not active")
                        continue  # IO point is not active

                    else:
                        # Retrieve data from corresponding table
                        timestamp_value_list_io = (
                            self.database_manager.get_io_point_value(
                                io_point_info[name]["io_id"],
                                io_type,
                            )
                        )

                        # Add to data dictionary
                        selected_data_manager.add_point(
                            name, timestamp_value_list_io
                        )

            except Exception as e:
                pass

        if vfd_points:
            try:

                vfd_point_info = {}  # vfd_readable_name: {vfdId: "", active: ""}

                # Get VFD Point info
                for vfd_point in vfd_points:

                    # Retrieve data from VFDConfig@0
                    vfd_point_info[vfd_point] = (
                        self.database_manager.get_vfd_point_info(vfd_point)
                    )

                    if vfd_point_info[vfd_point]["active"] == 0:
                        print(f"DEBUG: {vfd_point} was not active")
                        continue  # VFD point is not active

                    else:
                        # Retrieve data from corresponding table
                        timestamp_value_list_vfd = (
                            self.database_manager.get_vfd_point_value(
                                vfd_point_info[vfd_point]["vfd_id"],
                                VFD_POINTS[vfd_point]["type"],
                            )
                        )

                        # Flip bits if type is comms_wd_trip to stay consistent with devOk in Node Status Table
                        # For some reason in the comms_wd_trip column 1 means no comms and 0 means comms
                        if VFD_POINTS[vfd_point]["type"] == "comms_wd_trip":
                            flip_bits(timestamp_value_list_vfd)

                        # Add to data dictionary
                        selected_data_manager.add_point(
                            vfd_point, timestamp_value_list_vfd
                        )

            except Exception as e:
                pass

        if graph_presets:
            try:

                graph_preset_point_info = {}

                # Grab points behind preset
                for preset in graph_presets:
                    preset_points = GRAPH_PRESETS[preset]

                    # Iterate through each point
                    for entry in preset_points:
                        name = entry["name"]

                        # Determine if IO or VFD
                        if name in VFD_POINTS.keys():  # VFD

                            # Retrieve info from VFDConfig@0
                            graph_preset_point_info[name] = (
                                self.database_manager.get_vfd_point_info(name)
                            )

                            if graph_preset_point_info[name]["active"] == 0:
                                print(f"DEBUG: {name} not active - skipping Graph Preset")
                                break  # VFD point is not active - skip preset

                            else:
                                # Retrieve data from corresonding table
                                timestamp_value_list_preset = (
                                    self.database_manager.get_vfd_point_value(
                                        graph_preset_point_info[name]["vfd_id"],
                                        VFD_POINTS[name]["type"],
                                    )
                                )

                                # Add to data dictionary
                                selected_data_manager.add_preset(
                                    preset, name, timestamp_value_list_preset
                                )

                        else:  # IO
                            io_type = convert_io_type(entry["type"])

                            # Retrieve info from IOConfig
                            graph_preset_point_info[name] = (
                                self.database_manager.get_io_point_info(name, io_type)
                            )

                            if graph_preset_point_info[name]["active"] == 0:
                                print(f"DEBUG: {name} not active - skipping Graph Preset")
                                break  # IO point is not active - skip preset

                            else:
                                # Retrieve data from corresponding table
                                timestamp_value_list_preset = (
                                    self.database_manager.get_io_point_value(
                                        graph_preset_point_info[name]["io_id"],
                                        io_type,
                                    )
                                )

                                # Add to data dictionary
                                selected_data_manager.add_preset(
                                    preset, name, timestamp_value_list_preset
                                )
            except Exception as e:
                print(f"Error while adding points: {e}")

        if self.time_zone_offset:
            return enter_time_zone_offset(
                selected_data_manager.get_data(), self.time_zone_offset
            )
        else:
            self.time_zone_offset = self.database_manager.get_time_zone_offset()
            if self.time_zone_offset:
                return enter_time_zone_offset(
                    selected_data_manager.get_data(), self.time_zone_offset
                )
            else:
                offset_hours = self._ask_for_timezone_offset()
                self.time_zone_offset = offset_hours
                if offset_hours is not None:
                    return enter_time_zone_offset(
                        selected_data_manager.get_data(), offset_hours
                    )
                else:
                    return selected_data_manager.get_data()

    def _ask_for_timezone_offset(self) -> Optional[int]:
        """
        Ask user for timezone offset.

        Returns:
            int: Hours or None if cancelled.
        """

        try:
            from tkinter import simpledialog, messagebox
            import tkinter as tk

            report_info = self.database_manager.get_report_info()
            time_range_string = "Time Range Unavailable"

            if report_info:
                report_info = report_info[0]
                min_time = convert_timestamp_to_readable(report_info["first_timestamp"])
                max_time = convert_timestamp_to_readable(report_info["last_timestamp"])
                time_range_string = f"Time range currently spans from {min_time} - {max_time}"

            temp_root = tk.Tk()
            temp_root.withdraw()

            # Ask if user wants to enter offset
            wants_offset = messagebox.askyesno(
                "No Timezone Offset Parameter Found",
                "No timezone offset parameter was found in the database.\n\n"
                f"{time_range_string}\n\n"
                "Would you like to enter a custom timezone offset?",
                parent=temp_root,
            )

            if wants_offset:
                offset_hours = simpledialog.askinteger(
                    "Timezone Offset",
                    "Enter timezone offset in hours:\n"
                    "(e.g., 8 for +8 hours, or -5 for -5 hours)",
                    minvalue=-14,
                    maxvalue=14,
                    parent=temp_root,
                )
                temp_root.destroy()
                return offset_hours * 100  # Match representaion in database
            else:
                temp_root.destroy()
                return None
        except Exception as e:
            pass
            return None

    def generate_csv(self, data: dict) -> bool:
        """
        Generate CSV file of processed data.

        Parameters:
            data (dict): Dictionary containing data

        Returns:
            bool: True if generation successful, False otherwise
        """

        csv_generator = CSVGenerator()

        for category in data:
            if category == "preset":
                for preset_name, preset_data in data[category].items():

                    csv_headers = list(preset_data.keys())
                    csv_headers.insert(0, "Timestamp")
                    csv_generator.create_csv(preset_name + ".csv", csv_headers)
                    csv_generator.write_to_csv(preset_data)
            else:

                if data.get(category):

                    csv_headers = list(data[category].keys())
                    csv_headers.insert(0, "Timestamp")
                    csv_generator.create_csv("Custom.csv", csv_headers)
                    csv_generator.write_to_csv(data[category])

        return True

    def generate_graphs(
        self, data: dict, jna_current_limit: str, cutter_amp_limit: str
    ) -> list:
        """
        Plot data to Bokeh.

        Paramters:
            jna_current_limit (str): JNA Current Limit parameter
            cutter_amp_limit (str): Cutter Amp Limit parameter
        """
        graph_generator = GraphGenerator(data, jna_current_limit, cutter_amp_limit)
        graph_generator.generate_plots()

    def set_timezone_offset_ready(self):
        """Set timezone offset signal waiting thread to ready."""
        self.timezone_ready.set()

    def process_incidents(self) -> List[Dict]:
        """
        Pull all incidents from database and add them to the incident manager.

        Returns:
            List[Dict]: All incidents
        """

        # Create incident manager
        incident_manager = IncidentManager()

        # Configure manager to use the text dictionary
        incident_manager.set_xml_file()

        incident_manager.load_text_dic()

        # Load raw incidents into IncidentManager
        raw_incidents = self.database_manager.get_all_incidents()

        for incident in raw_incidents:
            incident_manager.add_db_entry(incident)

        # Clean raw incidents
        incident_manager.clean_data()

        if self.time_zone_offset:
            self.set_timezone_offset_ready()
            self.incidents_for_export =  apply_time_zone_offset_to_incidents(
                incident_manager.get_clean_incidents(), self.time_zone_offset
            )
            return self.incidents_for_export
        else:
            self.time_zone_offset = self.database_manager.get_time_zone_offset()
            if self.time_zone_offset:
                self.set_timezone_offset_ready()
                self.incidents_for_export = apply_time_zone_offset_to_incidents(
                    incident_manager.get_clean_incidents(), self.time_zone_offset
                )
                return self.incidents_for_export
            else:
                offset_hours = self._ask_for_timezone_offset()
                self.time_zone_offset = offset_hours
                if offset_hours is not None:
                    self.set_timezone_offset_ready()
                    self.incidents_for_export = apply_time_zone_offset_to_incidents(
                        incident_manager.get_clean_incidents(), offset_hours
                    )
                    return self.incidents_for_export
                else:
                    self.set_timezone_offset_ready()
                    self.incidents_for_export = incident_manager.get_clean_incidents()
                    return self.incidents_for_export

    def wait_for_timezone_offset(self) -> bool:
        """
        Wait for timezone offset to be set by another thread.

        Parameters:
            timeout (float): Maximum time to wait in seconds.

        Returns:
            bool: True if timezone was set, False if not
        """
        return self.timezone_ready.wait()

    def populate_report(self, params: Dict) -> None:
        """
        Populate report on incident viewer screen.

        Parameters:
            params (Dict): Dictionary containing UI components
        """

        report_info = self.database_manager.get_report_info()
        report_info = report_info[0]

        # Serial Number
        params["serial_num"].configure(
            text=f"Serial Number: LWS{str(report_info["id"])[3:]}"
        )

        # Generate dates
        start_timestamp = convert_timestamp_to_readable(report_info["first_timestamp"])
        end_timestamp = convert_timestamp_to_readable(report_info["last_timestamp"])

        if not self.time_zone_offset:
            offset = self.database_manager.get_time_zone_offset()
            if offset:
                pass
                self.time_zone_offset = offset
            else:
                pass
                if self.wait_for_timezone_offset():
                    pass
                else:
                    pass

        if self.time_zone_offset:
            new_timestamps = apply_time_zone_offset_to_report(
                [start_timestamp, end_timestamp], self.time_zone_offset
            )
            start_timestamp, end_timestamp = new_timestamps

        start_words = str(start_timestamp).split()
        end_words = str(end_timestamp).split()

        params["date"].configure(text=f"Date: {start_words[0]} - {end_words[0]}")

        params["time"].configure(text=f"Time: {start_words[1]} - {end_words[1]}")

    def export_incidents(self) -> None:
        """
        Export indients to a csv file.
        """

        incident_exporter = IncidentExorter(self.incidents_for_export)

        # Create CSV
        incident_exporter.create_csv()

        # Write to file
        incident_exporter.export_to_csv()

        # Open File for User
        open_file(os.path.join(DATA_FOLDER_PATH,ALARM_CSV_TITLE))

    def set_time_zone_offset(self, offset: Optional[int]):
        """Set timezone offset variable."""
        self.time_zone_offset = offset

        if offset is None:
            self.timezone_ready.clear()
        else:
            self.timezone_ready.set()

    def close_database_connections(self) -> None:
        """Close all database connections."""
        try:
            if hasattr(self, "database_manager") and self.database_manager:
                self.database_manager.close()

            if hasattr(self, "conn") and self.conn:
                self.conn.close()
                self.conn = None

            pass

        except Exception as e:
            pass

    def clear_cached_data(self) -> None:
        """Clear any cached database data."""
        self.merged_file = None
