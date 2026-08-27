"""Incident viewer component."""

import math
import customtkinter as ctk
import tkinter as tk
from tkinter import simpledialog
from typing import Callable, List, Dict


from config.ui_config import UI_PADDING, UI_COLORS, INCIDENTS_PER_PAGE, UI_FONTS


class IncidentViewer(ctk.CTkFrame):
    """Incident viewer component and search box."""

    def __init__(self, parent: ctk.CTkFrame, **kwargs):
        super().__init__(parent, **kwargs)
        self.callbacks = {}
        self.incident_listbox = None
        self.all_incidents = []
        self.current_display_list = []
        self.search_box = None
        self.search_var = None
        self.current_search_results = []  # Matching incidents for occurence search
        self.current_occurrence_index = 0
        self.search_mode = "text"
        self.search_timer = None
        self.search_delay = 300  # Milliseconds
        self.widget_pool = []
        self.active_widgets = []
        self.search_index = {}
        self.page_number = 1
        self.total_pages = 1
        self.setup_component()

    def setup_component(self) -> None:
        """Setup incident viewer and search box."""

        # Configure parent frame for grid
        self.grid_rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # Search box
        self.search_var = ctk.StringVar()
        self.search_box = ctk.CTkEntry(
            self,
            placeholder_text="search...",
            textvariable=self.search_var,
            border_width=2,
            fg_color="#252526",
            text_color=UI_COLORS["white"],
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
        )
        self.search_var.trace_add("write", self.on_search_changed)
        self.search_box.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Frame for incidents
        self.incident_listbox = ctk.CTkFrame(self)
        self.incident_listbox.propagate(False)
        self.incident_listbox.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Navigation Buttons Panel
        self.nav_panel = ctk.CTkFrame(self)
        self.nav_panel.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        self.page_number_text = ctk.CTkLabel(
            self.nav_panel,
            text=f"Page Number: {self.page_number}/{self.total_pages}",
            font=ctk.CTkFont(family="Inter", size=UI_FONTS["status"], weight="bold"),
        )
        self.page_number_text.pack(
            side = ctk.LEFT,
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Next navigation button
        self.next_btn = ctk.CTkButton(
            self.nav_panel,
            text="Next",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            fg_color=UI_COLORS["next"],
            hover_color=UI_COLORS["next_hover"],
            command=self.jump_to_next_page
        )
        self.next_btn.pack(
            side = ctk.RIGHT,
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Prev navigation button
        self.prev_btn = ctk.CTkButton(
            self.nav_panel,
            text="Previous",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            fg_color=UI_COLORS["prev"],
            hover_color=UI_COLORS["prev_hover"],
            command=self.jump_to_prev_page
        )
        self.prev_btn.pack(
            side = ctk.RIGHT,
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Jump to page button
        self.jump_to_page_btn = ctk.CTkButton(
            self.nav_panel,
            text="Jump",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            fg_color=UI_COLORS["jump"],
            hover_color=UI_COLORS["jump_hover"],
            command=self.ask_page_number
        )
        self.jump_to_page_btn.pack(
            side = ctk.RIGHT,
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

    def jump_to_next_page(self) -> None:
        """Jump to the next page of incidents."""
        if self.is_valid_page_number(self.page_number + 1):
            self.page_number += 1
            self.page_number_text.configure(text=f"Page Number: {self.page_number}/{self.total_pages}")
            self.render_incidents(self.current_display_list)

    def jump_to_prev_page(self) -> None:
        """Jump to the prev page of incidents."""
        if self.page_number > 1:
            self.page_number -= 1
            self.page_number_text.configure(text=f"Page Number: {self.page_number}/{self.total_pages}")
            self.render_incidents(self.current_display_list)

    def ask_page_number(self) -> None:
        """Asks user to type in a specific page number, then jumps to it."""
        temp_root = tk.Tk()
        temp_root.withdraw()
        page_number = None

        try:
            page_number = simpledialog.askinteger(
                "Jump to Page",
                "Enter Page Number:\n"
                "",
                minvalue=1,
                maxvalue=self.total_pages,
                parent=temp_root,
            )
        except Exception:
            pass

        temp_root.destroy()
        if page_number is not None:
            self.jump_to_page_number(page_number)

    def jump_to_page_number(self, page_number: int) -> None:
        """Jump to a specific page_number."""
        if not self.is_valid_page_number(page_number):
            return
        self.page_number = page_number
        self.page_number_text.configure(text=f"Page Number: {self.page_number}/{self.total_pages}")
        self.render_incidents(self.current_display_list)

    def is_valid_page_number(self, page_number) -> bool:
        """Validate page_number."""
        return 1 <= page_number <= math.ceil(len(self.current_display_list) / INCIDENTS_PER_PAGE)
    
    def get_page_number_from_index(self, index: int) -> int:
        """Returns the page number that an index of an incident lives on."""

        return (index // INCIDENTS_PER_PAGE) + 1

    def reset_page_number(self) -> None:
        """Resets page number back to page 1."""
        self.page_number = 1
        self.page_number_text.configure(text=f"Page Number: {self.page_number}/{self.total_pages}")

    def get_page_number(self) -> int:
        """Get page number."""
        return self.page_number

    def get_search_box(self) -> ctk.CTkEntry:
        """Get the components search box."""
        return self.search_box

    def get_search_var(self) -> ctk.StringVar:
        """Get the search box's string variable."""
        return self.search_var

    def populate_incidents(self, incidents: List[Dict]) -> None:
        """
        Populate the viewer with INCIDENTS_PER_PAGE num of incidents.

        Parameters:
            incidents (List[Dict]): All incidents
        """

        # Store all incidents
        self.all_incidents = incidents
        self.current_display_list = incidents

        # Setup Total Pages:
        #-------------------
        if len(incidents) % INCIDENTS_PER_PAGE == 0:
            self.total_pages = len(incidents) // INCIDENTS_PER_PAGE
        else:
            self.total_pages = (len(incidents) // INCIDENTS_PER_PAGE) + 1

        self.page_number_text.configure(text=f"Page Number: {self.page_number}/{self.total_pages}")

        self.build_search_index()

        # Render INCIDENTS_PER_PAGE number of incidents
        self.render_incidents(incidents)

    def build_search_index(self) -> None:
        """Build search index for faster searching."""
        self.search_index = {}

        for i, incident in enumerate(self.all_incidents):
            # Combine searchable text
            searchable_text = (
                f"{incident.get('text', '')} {incident.get('timestamp', '')}".lower()
            )

            words = searchable_text.split()
            for word in words:
                if word not in self.search_index:
                    self.search_index[word] = set()
                self.search_index[word].add(i)

    def fast_search(self, search_text: str) -> List[int]:
        """Fast search using pre-built index."""
        search_terms = search_text.lower().strip().split()
        if not search_terms:
            return list(range(len(self.all_incidents)))

        # Find incidents that match all search terms
        matching_incidents = None

        for term in search_terms:
            # Find incidents containing this term
            term_matches = set()

            # Check exact word matches first
            if term in self.search_index:
                term_matches.update(self.search_index[term])

            # Check partial word matches
            for word, incidents in self.search_index.items():
                if term in word:
                    term_matches.update(incidents)

            # Intersect with previous results
            if matching_incidents is None:
                matching_incidents = term_matches
            else:
                matching_incidents = matching_incidents.intersection(term_matches)

            # Early exit if no matches
            if not matching_incidents:
                break

        return sorted(list(matching_incidents or set()))

    def render_incidents(self, incidents: List[Dict]) -> None:
        """
        Render the specified incidents in the listbox.

        Parameters:
            incidents (List[Dict]): Incidents to display
        """

        for widget in self.active_widgets:
            widget.pack_forget()

        self.widget_pool.extend(self.active_widgets)
        self.active_widgets.clear()

        index = INCIDENTS_PER_PAGE * (self.page_number - 1)
        
        while index < (INCIDENTS_PER_PAGE * self.page_number) and index < len(incidents):
            incident_row = self.get_or_create_incident_widget()
            self.configure_incident_widget(incident_row, incidents[index], index)
            self.active_widgets.append(incident_row)
            index += 1

    def get_or_create_incident_widget(self):
        """Get widget from pool or create a new one."""
        if self.widget_pool:
            return self.widget_pool.pop()
        else:
            return self.create_incident_widget()

    def create_incident_widget(self):
        """Create a new incident widget structure."""
        incident_row = ctk.CTkFrame(self.incident_listbox, fg_color="transparent")
        incident_row.grid_columnconfigure(1, weight=1)

        # Create timestamp button
        timestamp_label = ctk.CTkButton(incident_row, corner_radius=0)
        timestamp_label.grid(row=0, column=0, sticky="w", padx=(5, 0), pady=2)

        # Create incident button
        incident_label = ctk.CTkButton(incident_row, corner_radius=0)
        incident_label.grid(row=0, column=1, sticky="ew", pady=2)

        # Store references for easy access
        incident_row.timestamp_btn = timestamp_label
        incident_row.incident_btn = incident_label

        return incident_row

    def configure_incident_widget(self, widget, incident, render_index):
        """Configure existing widget with new incident data."""
        # Update highlighting
        is_highlighted = self.should_highlight_incident(render_index, incident)
        bg_color = "yellow" if is_highlighted else "transparent"
        widget.configure(fg_color=bg_color)

        # Update timestamp button
        widget.timestamp_btn.configure(
            text=incident["timestamp"],
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            fg_color=incident["label_color"],
            hover_color=incident["label_color"],
            text_color=incident["text_color"],
            command=lambda: self.show_help_text(incident["help_text"]),
        )

        # Update incident button
        widget.incident_btn.configure(
            text=incident["text"],
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            fg_color=incident["label_color"],
            hover_color=incident["label_color"],
            text_color=incident["text_color"],
            command=lambda: self.show_help_text(incident["help_text"]),
        )

        # Show the widget
        widget.pack(fill="x", pady=2)

    def should_highlight_incident(self, render_index: int, incident: Dict) -> bool:
        """Determine if incident should be hightlighted."""
        if self.search_mode != "occurrence":
            return False

        if not self.current_search_results:
            return False

        actual_incident_index = render_index

        return (
            actual_incident_index in self.current_search_results
            and actual_incident_index
            == self.current_search_results[self.current_occurrence_index]
        )

    def on_search_changed(self, *args) -> None:
        """Handle search changes and filter incidents."""

        # Cancel existing
        if self.search_timer is not None:
            self.after_cancel(self.search_timer)

        # Set a new timer to execute after delay
        self.search_timer = self.after(self.search_delay, self.execute_search)

    def execute_search(self) -> None:
        """Execute a search after delay."""
        search_text = self.search_var.get().lower().strip()

        # Reset to first page when filtering
        self.page_number = 1
        self.page_number_text.configure(text=f"Page Number: {self.page_number}/{self.total_pages}")


        if not search_text:
            # Show all incidents if search is empty
            self.current_display_list = self.all_incidents
            self.render_incidents(self.all_incidents)
            self.current_search_results = []
            self.current_occurrence_index = 0
            return

        # Use fast indexed search
        matching_indices = self.fast_search(search_text)

        if self.search_mode == "text":

            # Text filtering mode = show only matching incidents
            filtered_incidents = [self.all_incidents[i] for i in matching_indices]
            # Re-render with filtered incidents
            self.current_display_list = filtered_incidents
            self.render_incidents(filtered_incidents)

        elif self.search_mode == "occurrence":
            # Occurence search mode = find all matches but show all incidents
            self.current_search_results = matching_indices
            self.current_occurrence_index = 0

            self.current_display_list = self.all_incidents
            self.render_incidents(self.all_incidents)

            # Highlight first occurrence
            if self.current_search_results:
                self.update_highlighting(-1, 0)
                incident_index = self.current_search_results[0]
                self.after(10, lambda: self.jump_to_incident(incident_index))

    def jump_to_occurrence(self, occurrence_index: int) -> None:
        """Jump to specific occurrence."""
        if not self.current_search_results or occurrence_index >= len(
            self.current_search_results
        ):
            return

        old_index = self.current_occurrence_index
        self.current_occurrence_index = occurrence_index

        # Update highlighting
        self.update_highlighting(old_index, occurrence_index)

        incident_index = self.current_search_results[occurrence_index]

        # Jump to the incident
        self.after(10, lambda: self.jump_to_incident(incident_index))


    def on_search_enter(self, event) -> None:
        """Handle Enter key in search box - jump to next occurrence."""
        if self.search_mode == "occurrence" and self.current_search_results:
            # Move to next occurrence
            next_index = (self.current_occurrence_index + 1) % len(
                self.current_search_results
            )
            self.jump_to_occurrence(next_index)

    def jump_to_incident(self, incident_index: int) -> None:
        """Jump to a specific page with a specific incident."""

        page_number = self.get_page_number_from_index(incident_index)

        if not self.is_valid_page_number(page_number):
            return
        
        self.jump_to_page_number(page_number)


    def set_search_mode(self, mode: str) -> None:
        """Set the search mode ('text' or 'occurrence')"""
        self.search_mode = mode

        if mode == "occurrence":
            # Bind enter key for occurrence search
            self.search_box.bind("<Return>", self.on_search_enter)
        else:
            # Unbind Enter key for text search
            self.search_box.unbind("<Return>")

        # Re-run search with new mode
        self.on_search_changed()

    def show_help_text(self, help_text: str) -> None:
        """
        Shows help text in a centered modal dialog.

        Parameters:
            help_text (str): Help text to display
        """

        if not help_text:
            return None

        # Create the modal dialog window
        help_dialog = ctk.CTkToplevel(self)
        help_dialog.title("Incident Help")
        help_dialog.geometry("500x300")
        help_dialog.resizable(False, False)

        # Make it modal (stays on top and blocks interaction with parent)
        help_dialog.transient(self.winfo_toplevel())
        help_dialog.grab_set()

        # Center the dialog on screen
        help_dialog.update_idletasks()
        x = (help_dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (help_dialog.winfo_screenheight() // 2) - (300 // 2)
        help_dialog.geometry(f"500x300+{x}+{y}")

        # Configure the dialog layout
        help_dialog.grid_rowconfigure(0, weight=1)
        help_dialog.grid_columnconfigure(0, weight=1)

        # Create scrollable text area for help content
        text_frame = ctk.CTkScrollableFrame(help_dialog)
        text_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 10))

        # Help text in a textbox (supports wrapping)
        help_textbox = ctk.CTkTextbox(
            text_frame,
            font=ctk.CTkFont(family="Inter", size=14),
            wrap="word",  # Wrap at word boundaries
            height=200,
            state="normal",  # Allow insertion of text
        )
        help_textbox.pack(fill="both", expand=True, padx=10, pady=10)

        # Insert the help text and make it read-only
        help_textbox.insert("1.0", help_text)
        help_textbox.configure(state="disabled")  # Make it read-only

        # Close button
        close_button = ctk.CTkButton(
            help_dialog,
            text="Close",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            command=help_dialog.destroy,
        )
        close_button.grid(row=1, column=0, pady=(10, 20))

    def update_highlighting(self, old_index: int, new_index: int) -> None:
        """Update highlighting without re-render."""
        page_start = INCIDENTS_PER_PAGE * (self.page_number - 1)
        page_end = page_start + INCIDENTS_PER_PAGE

        # Remove old highlight
        if old_index >= 0 and old_index < len(self.current_search_results):
            old_incident_idx = self.current_search_results[old_index]
            if page_start <= old_incident_idx < page_end:
                widget_index = old_incident_idx - page_start
                if widget_index < len(self.active_widgets):
                    self.active_widgets[widget_index].configure(fg_color="transparent")

        # Add new highlight
        if new_index >= 0 and new_index < len(self.current_search_results):
            new_incident_idx = self.current_search_results[new_index]
            if page_start <= new_incident_idx < page_end:
                widget_index = new_incident_idx - page_start
                if widget_index < len(self.active_widgets):
                    self.active_widgets[widget_index].configure(fg_color="yellow")

    def clear_incidents(self) -> None:
        """Clear all incidents from the viewer."""
        # Clear the display
        for widget in self.incident_listbox.winfo_children():
            widget.destroy()

        # Clear stored data
        self.all_incidents = []
        self.current_display_list = []
        self.current_search_results = []
        self.current_occurrence_index = 0

        # Clear search box
        if self.search_var:
            self.search_var.set("")

        self.search_mode = "text"

        if hasattr(self, "active_widgets"):
            self.active_widgets = []

        if hasattr(self, "widget_pool"):
            for widget in self.widget_pool:
                widget.destroy()
            self.widget_pool = []

    def set_callback(self, event_name: str, callback: Callable) -> None:
        """
        Set callback function for events.

        Parameters:
          event_name (str): Event name ('files_added', 'files_removed', 'files_cleared', 'selection_changed')
          callback (Callable): Callback function
        """

        self.callbacks[event_name] = callback
