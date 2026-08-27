"""Graph presets component."""

import customtkinter as ctk
from typing import Callable, List, Dict
from ui.components.selected import Selected

from config.point_mapping import GRAPH_PRESETS
from config.ui_config import UI_PADDING, UI_COLORS


class PresetGraph(ctk.CTkFrame):
    """Preset graph selection component."""

    def __init__(self, parent: ctk.CTkFrame, **kwargs):
        super().__init__(parent, **kwargs)
        self.state = {}
        self.callbacks = {}
        self.checkboxes = []

        self.setup_component()

    def setup_component(self):
        """Setup the preset graph selection interface."""

        # Create a frame for preset buttons
        componenet_listbox = ctk.CTkScrollableFrame(self, fg_color=UI_COLORS["frame"])
        componenet_listbox.pack(
            fill="both",
            expand=True,
            padx=UI_PADDING["medium"],
            pady=UI_PADDING["medium"],
        )
        componenet_listbox.grid_columnconfigure(0, weight=1)
        componenet_listbox.grid_columnconfigure(1, weight=1)

        row = 0

        # Create checkbox to select all presets
        all_presets_var = ctk.StringVar(value="off")
        self.state["All"] = all_presets_var
        all_presets_checkbox = ctk.CTkCheckBox(
            componenet_listbox,
            text="All",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            width=18,
            height=18,
            checkbox_width=16,
            checkbox_height=16,
            variable=all_presets_var,
            onvalue="on",
            offvalue="off",
            command=lambda k="All": self.on_all_toggle(k),
            fg_color=UI_COLORS["checkbox"],
            hover_color=UI_COLORS["checkbox_hover"],
            corner_radius=3,
            border_width=1,
            text_color=UI_COLORS["white"],
        )
        all_presets_checkbox.grid(
            row=row,
            column=0,
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
            sticky="ew",
        )

        self.checkboxes.append(all_presets_checkbox)
        row += 1

        # Populate frame with presets
        for key, value in GRAPH_PRESETS.items():
            preset_var = ctk.StringVar(value="off")
            self.state[key] = preset_var

            preset_checkbox = ctk.CTkCheckBox(
                componenet_listbox,
                text=key,
                font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                width=18,
                height=18,
                checkbox_width=16,
                checkbox_height=16,
                variable=preset_var,
                onvalue="on",
                offvalue="off",
                command=lambda k=key: self.on_preset_toggle(k),
                fg_color=UI_COLORS["checkbox"],
                hover_color=UI_COLORS["checkbox_hover"],
                corner_radius=3,
                border_width=1,
                text_color=UI_COLORS["white"],
            )
            preset_checkbox.grid(
                row=row,
                column=0,
                padx=UI_PADDING["small"],
                pady=UI_PADDING["small"],
                sticky="ew",
            )

            self.checkboxes.append(preset_checkbox)

            row += 1

    def on_preset_toggle(self, key: str) -> None:
        if self.state[key].get() == "on":
            Selected.add_preset(key)
        else:
            Selected.remove_preset(key)

    def on_all_toggle(self, all_key: str) -> None:

        for i, key in enumerate(self.state):
            if self.state[all_key].get() == "on":
                if key != "All": 
                    if self.state[key].get() == "on":
                        self.state[key].set("off")
                    else:
                        Selected.add_preset(key)
                    self.checkboxes[i].configure(state="disabled")
            else:
                if key != "All":
                    Selected.remove_preset(key)
                    self.checkboxes[i].configure(state="normal")

    def clear(self) -> None:
        """Clear all selected checboxes."""

        if self.state["All"].get() == "on":
            self.state["All"].set("off")
            self.on_all_toggle("All")
            if "cleared_graph_presets" in self.callbacks:
                self.callbacks["cleared_graph_presets"](len(self.state) - 1)
            return

        count = 0

        for key, var in self.state.items():
            if var.get() == "on":
                count += 1
                Selected.remove_preset(key)
            var.set("off")

        if "cleared_graph_presets" in self.callbacks:
            self.callbacks["cleared_graph_presets"](count)

    def get_selected_presets(self) -> List:
        """Get list of selected preset graphs."""

        # Check if all is selected
        if self.state["All"].get() == "on":
            return [key for key in self.state.keys() if key != "All"]
        else:
            return [key for key, var in self.state.items() if var.get() == "on"]

    def set_callback(self, event_name: str, callback: Callable) -> None:
        """
        Set callback function for events.

        Parameters:
          event_name (str): Event name ('files_added', 'files_removed', 'files_cleared', 'selection_changed')
          callback (Callable): Callback function
        """

        self.callbacks[event_name] = callback

    def disable_checkboxes(self):
        """Disable all checkboxes."""
        for checkbox in self.checkboxes:
            checkbox.configure(state="disabled")

    def enable_checkboxes(self):
        """Enable all checkboxes after processing."""
        for checkbox in self.checkboxes:
            checkbox.configure(state="normal")
