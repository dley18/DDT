from typing import List, Dict, Tuple, Any
import customtkinter as ctk

from config.ui_config import TYPE_COLORS, UI_COLORS, UI_PADDING, GRAPH_SEARCH_TYPES, MAX_POINTS_PER_SEARCH, SEARCH_TYPE_MAP
from ui.components.selected import Selected

class Search(ctk.CTkFrame):
    """Search component for additional io points"""

    def __init__(self, parent: ctk.CTkFrame, **kwargs):
        super().__init__(parent, **kwargs)
        self.all_io = None
        self.search_box = None
        self.search_var = None
        self.io_point_frame = None
        self.search_delay = 300 # Milliseconds
        self.checkboxes = []

        self.setup_componenet()

    def setup_componenet(self) -> None:
        """Initialize component"""

        self.grid_rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        search_box_frame = ctk.CTkFrame(self)
        search_box_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )
        search_box_frame.columnconfigure(1, weight=1)

        # Search Box
        search_box_label = ctk.CTkLabel(
            search_box_frame,
            text="Point Name: ",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color=UI_COLORS["white"],
        )
        search_box_label.grid(
            row=0,
            column=0,
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"]
        )

        self.search_var = ctk.StringVar()
        self.search_box = ctk.CTkEntry(
            search_box_frame,
            placeholder_text="",
            textvariable=self.search_var,
            border_width=2,
            fg_color="#252526",
            text_color=UI_COLORS["white"],
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
        )
        self.search_var.trace_add("write", self.on_search)
        self.search_box.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Type DropDown
        self.type_label = ctk.CTkLabel(
            search_box_frame,
            text="IO Type: ",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color=UI_COLORS["white"],
        )
        self.type_label.grid(
            row=0,
            column=2,
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        self.type_dropdown = ctk.CTkOptionMenu(
            search_box_frame,
            values=GRAPH_SEARCH_TYPES,
            fg_color=UI_COLORS["frame"],
            button_color=UI_COLORS["dropdown_btn"],
            button_hover_color=UI_COLORS["dropdown_btn_hover"],
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            command=self.on_dropdown_selection
        )
        self.type_dropdown.grid(
            row=0,
            column=3,
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        self.io_point_frame = ctk.CTkFrame(self)
        self.io_point_frame.propagate(False)
        self.io_point_frame.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )
        self.io_point_frame.columnconfigure(0, weight=1)

    def render_list(self, points_and_selected: List[Tuple[str, str, bool]]) -> None:
        """
        Renders a list of io points to the frame.

        Parameters:
            points_and_selected (List[Tuple(str, str, bool)]): List of points containing point name, its io type, and whether it has been selected
        """
        for widget in self.io_point_frame.winfo_children():
            widget.destroy()
        idx = 0
        while idx < MAX_POINTS_PER_SEARCH and idx < len(points_and_selected):
            name = points_and_selected[idx][0]
            io_type = str(points_and_selected[idx][1])
            selected = points_and_selected[idx][2]

            frame = ctk.CTkFrame(
                self.io_point_frame
            )
            frame.grid(
                row=idx,
                column=0,
                sticky="ew",
                padx=UI_PADDING["small"] - 1,
                pady=UI_PADDING["small"] - 1,
            )
            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(1, weight=0)
            point = ctk.CTkLabel(
                frame,
                text=name,
                font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
                fg_color=UI_COLORS["io_point_label"],
                corner_radius=5,
            )
            point.grid(
                row=0,
                column=0,
                sticky="ew",
                padx=UI_PADDING["small"] - 1,
                pady=UI_PADDING["small"] - 1,
            )

            btn = ctk.CTkButton(
                frame,
                text="Add" if not selected else "Remove" ,
                font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
                fg_color=UI_COLORS["add"] if not selected else UI_COLORS["remove"],
                hover_color=UI_COLORS["add_hover"] if not selected else UI_COLORS["remove_hover"],
                text_color=UI_COLORS["white"],
                width=75,
                corner_radius=5,
            )
            btn.grid(
                row=0,
                column=1,
                padx=UI_PADDING["small"] - 1,
                pady=UI_PADDING["small"] - 1,
            )
            btn.configure(
                command=lambda n=name, t=io_type, b=btn: self.on_toggle(n, t, b)
            )
            idx += 1

    def populate(self, points: List[Dict[str, Any]]) -> None:
        # Used once on initial render
        self.all_io = points
        for point in self.all_io:
            point["selected"] = False
            point["type"] = str(point["type"])
        self.render_list([
            (entry["name"], entry["type"], entry["selected"]) 
            for entry in points
        ])

    def on_search(self, *args):
        search_text = self.search_var.get().casefold()
        if self.type_dropdown.get() == "All":
            self.lowered_render_list = [(s["name"].casefold(), s) for s in self.all_io]
        else:
            self.lowered_render_list = [
                (s["name"].casefold(), s) 
                for s in self.all_io 
                if str(s["type"]) in SEARCH_TYPE_MAP[str(self.type_dropdown.get())]
            ]

        self.render_list(
            [(original["name"], original["type"], original["selected"]) 
            for lowered, original 
            in self.lowered_render_list 
            if search_text in lowered][:MAX_POINTS_PER_SEARCH]
        )

    def on_dropdown_selection(self, _):
        self.on_search()

    def on_toggle(self, name, io_type, button):
        entry = next(
        (item for item in self.all_io if item["name"] == name and item["type"] == io_type),
        None
        )
        if entry:
            if not entry["selected"] and Selected.already_selected(name, io_type, "IO"):
                return
            entry["selected"] = not entry["selected"]
            if entry["selected"]:
                button.configure(
                text="Remove",
                fg_color=UI_COLORS["remove"],
                hover_color=UI_COLORS["remove_hover"],
                )
                Selected.add_io(name, io_type)
            else:
                button.configure(
                    text="Add",
                    fg_color=UI_COLORS["add"],
                    hover_color=UI_COLORS["add_hover"],
                )
                Selected.remove_io(name, io_type)

    def clear_component(self) -> None:
        """Clears component"""
        self.populate([])

