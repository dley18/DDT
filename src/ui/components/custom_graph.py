"""Custom graph component to show a listbox of IO points for selection."""

from typing import Callable

import customtkinter as ctk
import math


from config.point_mapping import IO_POINTS, VFD_POINTS
from config.ui_config import SEARCH_TYPE_MAP, TYPE_COLORS, UI_PADDING, UI_COLORS
from ui.components.selected import Selected
from data.database_manager import DatabaseManager


class CustomGraph(ctk.CTkFrame):
    """Custom graph selection component."""

    def __init__(self, parent: ctk.CTkFrame, **kwargs):
        super().__init__(parent, **kwargs)
        self.io_state = {}
        self.vfd_state = {}
        self.callbacks = {}
        self.checkboxes = []

        self.setup_component()

    def setup_component(self) -> None:
        """Initialize component and fill with IO points."""

        self.component_listbox = ctk.CTkScrollableFrame(self)
        self.component_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        # Configure grid columns to expand equally
        self.component_listbox.grid_columnconfigure(0, weight=1)
        self.component_listbox.grid_columnconfigure(1, weight=1)

        self.left_column = ctk.CTkFrame(self.component_listbox)
        self.left_column.grid(row=0, column=0, padx=UI_PADDING["small"], pady=UI_PADDING["small"], sticky="nsew")
        self.right_column = ctk.CTkFrame(self.component_listbox)
        self.right_column.grid(row=0, column=1, padx=UI_PADDING["small"], pady=UI_PADDING["small"], sticky="nsew")

        self.frame_table = {}

        # Populate frame with IO points
        for key, value in IO_POINTS.items():
            if value["type"] not in self.frame_table:
                self.create_new_type_frame(value["type"])

            io_point_var = ctk.StringVar(value="off")
            self.io_state[key] = io_point_var
            io_point_checkbox = ctk.CTkCheckBox(
                self.frame_table[value["type"]],
                text=value["readable_name"],
                font=ctk.CTkFont(family="inter", size=14, weight="bold"),
                width=18,
                height=18,
                checkbox_width=16,
                checkbox_height=16,
                variable=io_point_var,
                onvalue="on",
                offvalue="off",
                command=lambda k=key, v=value: self.on_io_toggle(k, v),
                fg_color=UI_COLORS["checkbox"],
                hover_color=UI_COLORS["checkbox_hover"],
                corner_radius=3,
                border_width=1,
                text_color=UI_COLORS["white"],
            )
            io_point_checkbox.pack(
                side=ctk.TOP,
                padx=UI_PADDING["small"],
                pady=UI_PADDING["small"],
                fill="x"
            )
            self.checkboxes.append(io_point_checkbox)

        # Populate frame with VFD points
        self.create_new_type_frame("VFD")
        for key, value in VFD_POINTS.items():
            vfd_point_var = ctk.StringVar(value="off")
            self.vfd_state[key] = vfd_point_var
            vfd_point_checkbox = ctk.CTkCheckBox(
                self.frame_table["VFD"],
                text=key,
                font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                width=18,
                height=18,
                checkbox_width=16,
                checkbox_height=16,
                variable=vfd_point_var,
                onvalue="on",
                offvalue="off",
                command=lambda k = key, v = value: self.on_vfd_toggle(k, v),
                fg_color=UI_COLORS["checkbox"],
                hover_color=UI_COLORS["checkbox_hover"],
                corner_radius=3,
                border_width=1,
                text_color=UI_COLORS["white"],
            )
            vfd_point_checkbox.pack(
                side=ctk.TOP,
                padx=UI_PADDING["small"],
                pady=UI_PADDING["small"],
                fill="x"
            )
            self.checkboxes.append(vfd_point_checkbox)

    def create_new_type_frame(self, label_name: str) -> None:
        """Creates a new category frame for points to be added under"""

        parent = self.left_column if label_name == "AI" else self.right_column
        frame = ctk.CTkFrame(parent, fg_color=UI_COLORS["frame"])
        frame.pack(
            side=ctk.TOP,
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
            fill="both"
        )
        label = ctk.CTkLabel(
            frame,
            text=label_name,
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color=TYPE_COLORS[label_name],
            fg_color="black",
        ).pack(side=ctk.TOP, fill="x")

        self.frame_table[label_name] = frame

    def on_io_toggle(self, key: str, value: dict) -> None:
        """Add or remove from selected io frame"""
        is_on = self.io_state[key].get() == "on"
        io_type = None
        if DatabaseManager.get_database_version() == "1":
            io_type = SEARCH_TYPE_MAP[value["type"]][0]
        else:
            io_type = SEARCH_TYPE_MAP[value["type"]][1]

        if is_on:
            if Selected.already_selected(key, io_type, "IO"):
                print("Yes this was triggered")
                self.io_state[key].set(value="off")
                return
            Selected.add_io(key, io_type)
        else:
            Selected.remove_io(key, io_type)

    def on_vfd_toggle(self, key: str, value: dict) -> None:
        """Add or remove from selected vfd frame"""
        if self.vfd_state[key].get() == "on":
            Selected.add_vfd(key, "VFD")
        else:
            Selected.remove_vfd(key, "VFD")

    def clear(self) -> None:
        """Clear all selected checkboxes"""

        count = 0

        for key, var in self.io_state.items():
            if var.get() == "on":
                count += 1
                if DatabaseManager.get_database_version() == "1":
                    Selected.remove_io(key, SEARCH_TYPE_MAP[IO_POINTS[key]["type"]][0])
                else:
                    Selected.remove_io(key, SEARCH_TYPE_MAP[IO_POINTS[key]["type"]][1])
            var.set("off")
        for key, var in self.vfd_state.items():
            if var.get() == "on":
                count += 1
                Selected.remove_vfd(key, "VFD")
            var.set("off")

        if "cleared_custom_points" in self.callbacks:
            self.callbacks["cleared_custom_points"](count)

    def set_callback(self, event_name: str, callback: Callable) -> None:
        """
        Set callback function for events.

        Parameters:
          event_name (str): Event name ('files_added', 'files_removed', 'files_cleared', 'selection_changed')
          callback (Callable): Callback function
        """

        self.callbacks[event_name] = callback

    def disable_checkboxes(self):
        """Disable all checkboxes during processing."""
        for checkbox in self.checkboxes:
            checkbox.configure(state="disabled")

    def enable_checkboxes(self):
        """Enable all checkboxes after processing."""
        for checkbox in self.checkboxes:
            checkbox.configure(state="normal")
