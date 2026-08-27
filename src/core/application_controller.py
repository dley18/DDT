"""Application controller that coordinates UI and business logic."""

import threading
import gc

from config.constants import DATA_FOLDER_PATH, DATA_FOLDER_HOME
from core.workflow_manager import WorkflowManager
from data.database_manager import DatabaseManager
from ui.screen.main_window import MainWindow
from util.file_util import cleanup_data_directory, create_folder, get_xml_file


class ApplicationController:
    """Main application controller that coordinates UI and buisness logic."""

    def __init__(self):
        self.main_window = None
        self.database_manager = DatabaseManager()
        self.workflow_manager = WorkflowManager(self.database_manager)
        self.merged_file = None
        self.file_ready_event = threading.Event()

    def start_application(self) -> None:
        """Start the main application"""
        try:
            # Create data folder
            create_folder(DATA_FOLDER_PATH)

            # Create main window
            print("DEBUG: Creating MainWindow - from {application_controller.start_application}")
            self.main_window = MainWindow()
            print("DEBUG: MainWindow created - from {application_controller.start_application}")

            # Set up UI callbacks
            self.setup_ui_callbacks()
            print("DEBUG: UI Callbacks Ready - from {application_controller.start_application}")

            # Start main loop
            print("DEBUG: Entering Mainloop - from {application_controller.start_application}")
            self.main_window.run()
            print("DEBUG: Mainloop exited - from {application_controller.start_application}")

        except Exception as e:
            # Do NOT swallow startup errors; write a log so packaged exe isn't silent
            try:
                import os, traceback
                from util.file_util import ensure_directory_exists

                ensure_directory_exists(DATA_FOLDER_HOME)
                log_path = os.path.join(DATA_FOLDER_HOME, "startup_error.log")
                with open(log_path, "w", encoding="utf-8") as f:
                    f.write("DDT failed to start due to an exception.\n\n")
                    traceback.print_exc(file=f)
                    f.write("\nMessage: " + str(e) + "\n")
                # Best-effort user hint via console if available
                print(f"Startup error written to: {log_path}")
            except Exception:
                # If even logging fails, re-raise so outer handler can capture
                pass
            # Re-raise to let outer handler report/exit appropriately
            raise

    def setup_ui_callbacks(self) -> None:
        """Set up callbacks for UI events."""
        if not self.main_window:
            return

        # File selection callbacks
        self.main_window.set_callback("files_added", self.on_files_added)
        self.main_window.set_callback("files_removed", self.on_files_removed)
        self.main_window.set_callback("files_cleared", self.on_files_cleared)
        self.main_window.set_callback("data_folder_opened", self.on_data_folder_opened)
        self.main_window.set_callback(
            "close_database_connections", self.close_database_connections
        )
        self.main_window.set_callback("database_deleted", self.on_database_deleted)

        # Graphing callbacks
        self.main_window.set_callback(
            "cleared_custom_points", self.on_cleared_custom_points
        )
        self.main_window.set_callback(
            "cleared_graph_presets", self.on_cleared_graph_presets
        )
        self.main_window.set_callback("generate_graphs", self.on_generate_graphs)

        # Incident callbacks
        self.main_window.set_callback("populate_incidents", self.on_populate_incidents)
        self.main_window.set_callback("populate_report", self.on_populate_report)
        self.main_window.set_callback("export_incidents", self.on_export_incidents)

    def on_files_added(self, count: int, params: dict) -> None:
        """Handle files added event."""
        try:
            self.file_ready_event.clear()
            thread = threading.Thread(
                target=self._files_added_background,
                args=(params,),
                name="FileLoading",
            )
            thread.daemon = True
            thread.start()
        except Exception as e:
            self.main_window.update_status(f"Error: {e}")

    def on_files_removed(self, count: int) -> None:
        """Handle files removed event."""
        try:
            self.merged_file = ""

        except Exception as e:
            if self.main_window:
                self.main_window.update_status(f"Error processing removed files: {e}")

    def on_files_cleared(self, count: int) -> None:
        """Handle files cleared event."""
        try:
            self.merged_file = ""

        except Exception as e:
            if self.main_window:
                self.main_window.update_status(f"Error processing cleared files: {e}")

    def on_data_folder_opened(self) -> None:
        """Handle data folder opened."""
        try:
            # Log or process data folder opening
            pass
            # Additional business logic could go here
            
        except Exception as e:
            if self.main_window:
                self.main_window.update_status(f"Error opening data folder: {e}")

    def close_database_connections(self) -> None:
        """Close all open connections before deletion."""
        try:
            pass

            # Close WorkflowManager connections
            if self.workflow_manager:
                if hasattr(self.workflow_manager, "close_database_connections"):
                    self.workflow_manager.close_database_connections()

            # Close any direct connections
            if hasattr(self, "database_manager") and self.database_manager:
                self.database_manager.close()

            gc.collect()

            pass
        except Exception as e:
            pass

    def on_database_deleted(self) -> None:
        """Handle deletion of main database."""

        self.merged_file = None

        if self.workflow_manager:
            if hasattr(self.workflow_manager, "clear_cached_data"):
                self.workflow_manager.clear_cached_data()

    def on_cleared_custom_points(self, count: int) -> None:
        """Handle cleared custom points event."""
        try:
            # Log points clearing
            pass

        except Exception as e:
            if self.main_window:
                self.main_window.update_status(f"Error processing cleared points: {e}")

    def on_cleared_graph_presets(self, count: int) -> None:
        """Handle cleared presets event."""
        try:
            # Log clearing
            pass

        except Exception as e:
            if self.main_window:
                self.main_window.update_status(f"Error processing cleared presets: {e}")

    def on_generate_graphs(self, params: dict) -> None:
        """Handle graph generation request with collected parameters."""

        try:
            self.file_ready_event.clear()
            thread = threading.Thread(
                target=self._generate_graphs_background,
                args=(params,),
                name="GraphGeneration",
            )
            thread.daemon = True
            thread.start()
        except Exception as e:
            self.main_window.update_status(f"Error: {e}")

    def on_populate_incidents(self, params: dict) -> None:
        """Handle incident population request."""

        try:
            thread = threading.Thread(
                target=self._populate_incidents_background,
                args=(params,),
                name="IncidentPopulation",
            )
            thread.daemon = True
            thread.start()
        except Exception as e:
            self.main_window.update_status(f"Error: {e}")

    def on_populate_report(self, params: dict) -> None:
        """Handle populate request from incident viewer screen."""

        try:
            self.file_ready_event.clear()
            thread = threading.Thread(
                target=self._populate_report_background,
                args=(params,),
                name="ReportPopulation",
            )
            thread.daemon = True
            thread.start()
        except Exception as e:
            self.main_window.update_status(f"Error: {e}")

    def on_export_incidents(self) -> None:
        """Handle export request from incident viewer."""

        try:
            thread = threading.Thread(
                target=self._export_incidents_background,
                name="IncidentExport",
            )
            thread.daemon = True
            thread.start()
        except Exception as e:
            self.main_window.update_status(f"Error: {e}")

    def _files_added_background(self, params: dict) -> None:
        """Background thread that triggers after adding files."""
        try:
            self.start_progress_bar()
            if self.merged_file is None:
                # Load, extract, and merge LZ4's
                self._update_ui_safe("Extracting archive...")

                if params["files"]:
                    print("DEBUG: Merging Files - from {workflow_manager.load_files}")
                    self.merged_file = self.workflow_manager.load_files(params["files"])
                    self.file_ready_event.set()
                    points = self.workflow_manager.pull_io_points()
                    params["search_panel"].populate(points)
                    self.workflow_manager.set_time_zone_offset(None)
                else:
                    self._update_ui_safe("No files selected on Home Screen")
                    self.workflow_manager.set_time_zone_offset(None)

                # Check if file loaded
            if self.merged_file != "":
                self._update_ui_safe("Files loaded")
                self.main_window.enable_database_deletion()
                self.main_window.enable_graphing_btns()
                self.main_window.enable_incident_population()
            else:
                self._update_ui_safe("Failed to load merged file")

            self.stop_progress_bar()

        except Exception as e:
            self.stop_progress_bar()
            self._update_ui_safe(f"An error occured when extracting archive: {e}")

    def _generate_graphs_background(self, params: dict) -> None:
        """Background thread for graph generation."""
        try:
            self.start_progress_bar()
            # Check if file has previously been created
            if self.merged_file is None:
                self._update_ui_safe("No files selected on Home screen.")
                self.main_window.enable_graphing_btns()
                self.stop_progress_bar()
                return

            # Check if file loaded
            if self.merged_file != "":
                self._update_ui_safe("Files loaded")
                self.main_window.enable_database_deletion()
            else:
                self._update_ui_safe("Failed to load merged file")

            # Stage 2: Data processing (40% progress)
            self._update_ui_safe("Processing data...")
            print("DEBUG: Creating Data Dict - from {workflow_manager.process_data}")
            if params["io_points"] or params["vfd_points"] or params["preset_graphs"]:
                processed_data = self.workflow_manager.process_data(
                    params["io_points"],
                    params["vfd_points"],
                    params["preset_graphs"],
                )
                self._update_ui_safe("Data processed...")
            else:
                self._update_ui_safe("No points or graphs selected for plotting.")
                self.main_window.enable_graphing_btns()
                self.stop_progress_bar()
                return

            # Stage 3: Generate CSV (optional 60% progess)
            if params["include_csv"] is True:
                print("DEBUG: Generating CSV File - from {workflow_manager.gernate_csv}")
                self._update_ui_safe("Generating CSV File...")
                self.workflow_manager.generate_csv(processed_data)
                self._update_ui_safe("CSV Generated")

            # Stage 4: Graph data to Bokeh plots (80% progress)
            self._update_ui_safe("Creating plots...")
            print("DEBUG: Generating Graphs - from {workflow_manager.generate_graphs}")
            self.workflow_manager.generate_graphs(
                processed_data, params["jna_current_limit"], params["cutter_amp_limit"]
            )
            self._update_ui_safe("Plots generated...")

            # Stage 5: Clean up directory (100% progress)
            self._update_ui_safe("Cleaning directory...")
            cleanup_data_directory()
            self._update_ui_safe("Task complete.")
            print("DEBUG: Background Tasks Complete - from {application_controller._generate_graphs_background}")

            # Re-enable graphing buttons
            self.main_window.enable_graphing_btns()
            self.stop_progress_bar()

        except Exception as e:
            self.stop_progress_bar()
            self._update_ui_safe(f"An error occured when generating graphs: {e}")

    def _populate_incidents_background(self, params: dict) -> None:
        """Background thread for incident population."""

        # Check if file has previously been created
        self.start_progress_bar()
        if self.merged_file is None:
            self.stop_progress_bar()
            self._update_ui_safe("No files selected on Home screen.")
            self.main_window.enable_incident_population()
            return

        self.file_ready_event.set()

        # Check if text dictionary exists
        if get_xml_file() is not None:

            self._update_ui_safe("Processing incidents...")
            # Stage 2: Proccess incidents in DB
            print("DEBUG: Adding Incidents to the Incident Manager - from {workflow_manager.process_incdients}")
            incidents = self.workflow_manager.process_incidents()

            self._update_ui_safe("Rendering incidents...")
            print("DEBUG: Rendering Incidents - from {incident_viewer.populate_incidents}")
            # Stage 3: Pass incidents to component for rendering
            params["incident_viewer"].populate_incidents(incidents)

            self._update_ui_safe("Population complete.")
            print("DEBUG: Background Tasks Complete - from {application_controller._populate_incidents_background}")


            # Enable export button
            params["export_button"].configure(state="normal")
            self.stop_progress_bar()

        else:  # No text dictionary was found
            self.stop_progress_bar()
            self._update_ui_safe("Data download did not contain a text dictionary")

    def _populate_report_background(self, params: dict) -> None:
        """Background thread for report population."""

        if not self.merged_file:
            self.file_ready_event.wait()  # Block until file creation

        self.workflow_manager.populate_report(params)

    def _export_incidents_background(self) -> None:
        """Background thread for exporting incidents."""
        self._update_ui_safe("exporting to csv file...")
        self.workflow_manager.export_incidents()
        self._update_ui_safe("Export Complete")

    def start_progress_bar(self) -> None:
        """Turn on the progress bar and set to intermediate mode."""

        self.main_window.components["footer"]["progress"].configure(mode="indeterminate", indeterminate_speed=0.5)
        self.main_window.components["footer"]["progress"].start()

    def stop_progress_bar(self) -> None:
        self.main_window.components["footer"]["progress"].stop()

    def _update_ui_safe(self, message: str) -> None:
        """
        Safely update UI from background thread.

        Parameters:
            message (str): Message to display to UI
            progress (float): Value from 0 - 1 to set progress bar
        """

        def update():
            self.main_window.update_status(message)

        self.main_window.root.after(0, update)


def create_application() -> ApplicationController:
    """
    Create and return a new application instance.

    Returns:
      ApplicationController: New application controller instance
    """
    return ApplicationController()


def run_application() -> None:
    """Run DDT application."""
    try:
        app = create_application()
        app.start_application()
    except Exception as e:
        # Log to user's Documents/DDT for visibility in both dev and packaged exe
        try:
            import os, traceback
            from util.file_util import ensure_directory_exists

            ensure_directory_exists(DATA_FOLDER_HOME)
            log_path = os.path.join(DATA_FOLDER_HOME, "startup_error.log")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write("\n=== Application start failure ===\n")
                traceback.print_exc(file=f)
                f.write("\nMessage: " + str(e) + "\n")
            print(f"Startup error written to: {log_path}")
        except Exception:
            pass
        # Re-raise so a console build also shows the error
        raise
