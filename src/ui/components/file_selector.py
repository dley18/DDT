"""File selector component for selecting data download files."""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable, List

from config.ui_config import UI_COLORS
import customtkinter as ctk

from util.file_util import get_file_size, cleanup_data_directory
from util.validation import validate_file_exists, validate_file_extension
from config.constants import DATA_FOLDER_PATH


class FileSelector(ctk.CTkFrame):
    """File selection component with list and management buttons."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.selected_files = []
        self.callbacks = {}

        self.setup_ui()

    def setup_ui(self) -> None:
        """Create the file selector UI components."""
        # Configure grid widgets
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Main container
        container = ctk.CTkFrame(self)
        container.grid(row=0, column=0, stick="nsew", padx=10, pady=10)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # File list with scrollbar
        self.file_listbox = tk.Listbox(
            container,
            selectmode=tk.EXTENDED,
            font=("Consolas", 20),
            bg=UI_COLORS["frame"],
            fg="#ffffff",
            selectbackground="#1f538d",
            activestyle="none",
        )

        # Scrollbar for listbox
        scrollbar = ctk.CTkScrollbar(container, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)

        # Grid layout
        self.file_listbox.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        scrollbar.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)

        # Bind events
        self.file_listbox.bind("<Double-Button-1>", self.on_double_click)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_selection_changed)

    def add_files(self, file_paths: List[str] = None) -> None:
        """
        Add files to the selection list.

        Parameters:
          file_paths (List[str], optional): File paths to add, or None to show file dialog
        """

        has_db_files, db_files = self.has_database_files_in_data_folder()

        if has_db_files:
            file_list = "\n".join(db_files)
            messagebox.showerror(
                "Previously processed database files found",
                f"Cannot add new files while processed database files exist.\n\n"
                f"Please delete the existing database files first: \n{file_list}\n\n"
                f"Use the 'Delete Data Folder Contents' button to remove them.",
            )
            return

        if file_paths is None:
            # Show file dialog
            file_paths = filedialog.askopenfilenames(
                title="Select Database Files",
                filetypes=[
                    ("All Supported", "*.db;*.sqlite;*.sqlite3;*.lz4"),
                    ("Database files", "*.db;*.sqlite;*.sqlite3"),
                    ("LZ4 compressed", "*.lz4"),
                    ("All files", "*."),
                ],
            )

        if not file_paths:
            return

        added_count = 0
        for file_path in file_paths:
            if self.add_single_file(file_path):
                added_count += 1

        if added_count > 0:
            self.refresh_display()
            if "files_added" in self.callbacks:
                self.callbacks["files_added"](added_count)

    def add_single_file(self, file_path: str) -> bool:
        """
        Add a single file to the selection.

        Parameters:
          file_path(str): Path to the file to add

        Returns:
          bool: True if file was added, False otherwise
        """

        has_db_files, db_files = self.has_database_files_in_data_folder()

        if has_db_files:
            file_list = "\n".join(db_files)
            messagebox.showerror(
                "Previously processed database files found",
                f"Cannot add new files while processed database files exist.\n\n"
                f"Please delete the existing database files first: \n{file_list}\n\n"
                f"Use the 'Delete Data Folder Contents' button to remove them.",
            )
            return

        # Validate file
        if not validate_file_exists(file_path):
            messagebox.showerror("Error", f"File does not exist: {file_path}")
            return False

        # Check if already in list
        if file_path in self.selected_files:
            messagebox.showerror(
                "Warning", f"File already in list: {os.path.basename(file_path)}"
            )
            return False

        # Validate file extension (optional)
        valid_extensions = [".db", ".sqlite", ".sqlite3", ".lz4"]
        is_valid, error_msg = validate_file_extension(file_path, valid_extensions)
        if not is_valid:
            result = messagebox.askyesno("Warning", f"{error_msg}\n\nAdd file anyway?")
            if not result:
                return False

        # Add to list
        self.selected_files.append(file_path)
        return True

    def remove_selected_files(self) -> None:
        """Remove currently selcted files from the list."""
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("Info", "No files selected for removal.")
            return

        # Remove files (reverse order to maintain indices)
        removed_count = 0
        for index in reversed(selected_indices):
            if 0 <= index < len(self.selected_files):
                self.selected_files.pop(index)
                removed_count += 1

        self.refresh_display()

        if removed_count > 0 and "files_removed" in self.callbacks:
            self.callbacks["files_removed"](removed_count)

    def clear_all_files(self, force=False) -> None:
        """Clear all files from the selection."""
        if not self.selected_files:
            messagebox.showinfo("Info", "No files to clear.")
            return

        if not force:
            result = messagebox.askyesno(
                "Confirm", f"Remove all {len(self.selected_files)} files from the list?"
            )
        else:
            result = force

        if result:
            count = len(self.selected_files)
            self.selected_files.clear()
            self.refresh_display()

            if "files_cleared" in self.callbacks:
                self.callbacks["files_cleared"](count)

    def open_data_folder(self) -> None:
        """Open data folder."""
        os.startfile(DATA_FOLDER_PATH)
        
        if "data_folder_opened" in self.callbacks:
            self.callbacks["data_folder_opened"]()

    def delete_database_file(self) -> None:
        """Delete merged database file."""

        files_in_directory = os.listdir(DATA_FOLDER_PATH)

        if not files_in_directory:
            messagebox.showinfo("Info", "No files found to delete.")
            return

        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the data folder contents?\n\n{DATA_FOLDER_PATH}",
        )

        if not result:
            return

        try:
            # Step 1: Request connection closure
            if "database_closing" in self.callbacks:
                self.callbacks["database_closing"]()

            # Step 2: Wait for cleanup, then attempt deletion
            self.after(300, self._attempt_file_deletion)

        except Exception as e:
            messagebox.showerror("Error", f"Error preparing file deletion: {e}")

    def _attempt_file_deletion(self) -> None:
        """Attempt to delete the database file after cleanup."""
        try:
            # Delete the main database file
            if os.path.exists(DATA_FOLDER_PATH):
                for filename in os.listdir(DATA_FOLDER_PATH):
                    if (
                        filename.endswith(".db")
                        or filename.endswith(".sqlite")
                        or filename.endswith(".xml")
                    ):
                        file_path = os.path.join(DATA_FOLDER_PATH, filename)
                        try:
                            os.remove(file_path)
                            pass
                        except Exception as e:
                            pass

            if "database_deleted" in self.callbacks:
                self.callbacks["database_deleted"]()

            messagebox.showinfo("Success", "Database files deleted successfully.")

        except PermissionError:
            messagebox.showerror(
                "File in Use",
                "Cannot delete file - it's currently being used.\n\n"
                "Please wait for any running operations to complete and try again.",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting files {e}")

    def refresh_display(self) -> None:
        """Refresh the file list display."""
        # Clear current display
        self.file_listbox.delete(0, tk.END)

        # Add files with formatted display
        for file_path in self.selected_files:
            display_text = self.format_file_display(file_path)
            self.file_listbox.insert(tk.END, display_text)

    def format_file_display(self, file_path: str) -> str:
        """
        Format file path for display in the list.

        Parameters:
          file_path (str): File path to format

        Returns:
          str: Formattd display string
        """

        file_name = os.path.basename(file_path)
        file_size = get_file_size(file_path)

        # Format size
        if file_size > 1024 * 1024:  # 1MB
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        elif file_size > 1024:  # > 1KB
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size} B"

        # Format display string (filename + size)
        return f"{file_name:<50} ({size_str})"

    def get_selected_files(self) -> List[str]:
        """
        Get list of selected file paths.

        Returns:
          List[str]: List of selected file paths
        """

        return self.selected_files.copy()

    def get_selected_count(self) -> int:
        """
        Get number of selcted files.

        Returns:
          int: Number of selected files
        """

        return len(self.selected_files)

    def set_callback(self, event_name: str, callback: Callable) -> None:
        """
        Set callback function for events.

        Parameters:
          event_name (str): Event name ('files_added', 'files_removed', 'files_cleared', 'selection_changed')
          callback (Callable): Callback function
        """

        self.callbacks[event_name] = callback

    def on_double_click(self, event) -> None:
        """Handle double-click on file list item."""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.selected_files):
                file_path = self.selected_files[index]
                self.show_file_info(file_path)

    def on_selection_changed(self, event) -> None:
        """Handle selection change in file list."""
        if "selection_changed" in self.callbacks:
            selected_indices = self.file_listbox.curselection()
            self.callbacks["selection_changed"](selected_indices)

    def show_file_info(self, file_path: str) -> None:
        """
        Show detailed information about a file.

        Parameters:
          file_path (str): Path to the file
        """

        if not validate_file_exists(file_path):
            messagebox.showerror("Error", "File no longer exists.")
            return

        # Gather file information
        filename = os.path.basename(file_path)
        directory = os.path.dirname(file_path)
        file_size = get_file_size(file_path)

        try:
            modified_time = os.path.getmtime(file_path)
            import datetime

            modified_str = datetime.datetime.fromtimestamp(modified_time).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        except:
            modified_str = "Unknown"

        # Format size
        if file_size > 1024 * 1024:
            size_str = f"{file_size / (1024 * 1024):.2f} MB ({file_size:,} bytes)"
        elif file_size > 1024:
            size_str = f"{file_size / 1024:.2f} KB ({file_size:,} bytes)"
        else:
            size_str = f"{file_size} bytes"

        # Show info dialog
        info_text = f"""Info:

Name: {filename}
Directory: {directory}
Size: {size_str}
Modified: {modified_str}
Full Path: {file_path}"""

        messagebox.showinfo("File information", info_text)

    def validate_all_files(self) -> List[str]:
        """
        Validate all files in the selection.

        Returns:
          List[str]: List of invalid file paths.
        """
        invalid_files = []

        for file_path in self.selected_files:
            if not validate_file_exists(file_path):
                invalid_files.append(file_path)

        return invalid_files

    def remove_invalid_files(self) -> int:
        """
        Remove invalid files from the selection.

        Returns:
          int: Number of files removed
        """

        invalid_files = self.validate_all_files()

        if not invalid_files:
            return 0

        # Remove invalid files
        for file_path in invalid_files:
            if file_path in self.selected_files:
                self.selected_files.remove(file_path)

        self.refresh_display()
        return len(invalid_files)

    def has_database_files_in_data_folder(self) -> tuple[bool, list]:
        """
        Check if data folder contains database files.

        Returns:
            tuple: (has_db_files, list_db_files)
        """
        if not os.path.exists(DATA_FOLDER_PATH):
            return False, []

        try:
            database_files = []
            for filename in os.listdir(DATA_FOLDER_PATH):
                if (
                    filename.endswith(".db")
                    or filename.endswith(".sqlite")
                    or filename.endswith(".xml")
                ):
                    database_files.append(filename)

            return len(database_files) > 0, database_files
        except OSError:
            return False, []
