from config.ui_config import UI_PADDING, UI_COLORS, TYPE_COLORS, SEARCH_TYPE_MAP
import customtkinter as ctk

class Selected(ctk.CTkFrame):
    """Viewer for selected Points/Presets"""

    selected_io_points = []
    selected_vfd_points = []
    selected_presets = []
    main_frame = None
    io_frame = None
    vfd_frame = None
    preset_frame = None

    def __init__(self, parent: ctk.CTkFrame, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_component()

    def setup_component(self) -> None:
        self.columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        Selected.main_frame = ctk.CTkFrame(self)
        Selected.main_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )
        Selected.main_frame.rowconfigure(1, weight=1)
        Selected.main_frame.columnconfigure(0, weight=1, uniform="selected")
        Selected.main_frame.columnconfigure(1, weight=1, uniform="selected")
        Selected.main_frame.columnconfigure(2, weight=1, uniform="selected")


        # Frame for IO Points
        Selected.io_frame = ctk.CTkScrollableFrame(
            Selected.main_frame,
            border_width=3,
            corner_radius=5,
            border_color=UI_COLORS["io_point_label"],
        )
        Selected.io_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )
        Selected.io_frame.columnconfigure(0, weight=1)
        # Adjust Scrollbar
        ctk.CTkScrollbar.grid_configure(Selected.io_frame._scrollbar, padx=5)

        io_label = ctk.CTkLabel(
            Selected.main_frame,
            text="IO",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color=UI_COLORS["white"],
        )
        io_label.grid(
            row=0,
            column=0,
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Frame for VFD Points
        Selected.vfd_frame = ctk.CTkScrollableFrame(
            Selected.main_frame,
            border_width=3,
            corner_radius=5,
            border_color=UI_COLORS["io_point_label"],
        )
        Selected.vfd_frame.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        Selected.vfd_frame.columnconfigure(0, weight=1)
        # Adjust Scrollbar
        ctk.CTkScrollbar.grid_configure(Selected.vfd_frame._scrollbar, padx=5)

        vfd_label = ctk.CTkLabel(
            Selected.main_frame,
            text="VFD",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color=UI_COLORS["white"],
        )
        vfd_label.grid(
            row=0,
            column=1,
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Frame for presets
        Selected.preset_frame = ctk.CTkScrollableFrame(
            Selected.main_frame,
            border_width=3,
            corner_radius=5,
            border_color=UI_COLORS["io_point_label"],
        )
        Selected.preset_frame.grid(
            row=1,
            column=2,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )
        Selected.preset_frame.columnconfigure(0, weight=1)
        # Adjust Scrollbar
        ctk.CTkScrollbar.grid_configure(Selected.preset_frame._scrollbar, padx=5)

        preset_label = ctk.CTkLabel(
            Selected.main_frame,
            text="Presets",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color=UI_COLORS["white"],
        )
        preset_label.grid(
            row=0,
            column=2,
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

    @staticmethod
    def already_selected(name: str, point_type: str, frame_type: str) -> bool:
        target_list = None
        if frame_type == "IO":
            target_list = Selected.selected_io_points
        elif frame_type == "VFD":
            target_list = Selected.selected_vfd_points
        else:
            target_list = Selected.selected_presets

        return {"name": name, "type": point_type} in target_list

    @staticmethod
    def add_io(name: str, point_type: str) -> None:
        Selected.selected_io_points.append({"name": name, "type": point_type})
        Selected._refresh("io")

    @staticmethod
    def add_vfd(name: str, point_type="VFD") -> None:
        Selected.selected_vfd_points.append({"name": name, "type": point_type})
        Selected._refresh("vfd")

    @staticmethod
    def add_preset(name: str, point_type="PRESET") -> None:
        Selected.selected_presets.append({"name": name, "type": point_type})
        Selected._refresh("preset")

    @staticmethod
    def remove_io(name: str, point_type: str) -> None:
        Selected.selected_io_points.remove({"name": name, "type": point_type})
        Selected._refresh("io")

    @staticmethod
    def remove_vfd(name: str, point_type="VFD") -> None:
        Selected.selected_vfd_points.remove({"name": name, "type": point_type})
        Selected._refresh("vfd")

    @staticmethod
    def remove_preset(name: str, point_type="PRESET") -> None:
        Selected.selected_presets.remove({"name": name, "type": point_type})
        Selected._refresh("preset")

    @staticmethod
    def _create_labels(type: str) -> None:
        frame = None
        points = None
        if type == "io":
            frame = Selected.io_frame
            points = Selected.selected_io_points
        elif type == "vfd":
            frame = Selected.vfd_frame
            points = Selected.selected_vfd_points
        else: 
            frame = Selected.preset_frame
            points = Selected.selected_presets

        row = 0
        for item in points:
            point_frame = ctk.CTkFrame(frame)
            point_frame.grid(
                row=row,
                column=0,
                sticky="ew",
                padx=UI_PADDING["small"] - 1,
                pady=UI_PADDING["small"] - 1,
            )
            point_frame.columnconfigure(0, weight=1)
            point_frame.columnconfigure(1, weight=0)
            ctk.CTkLabel(
                point_frame,
                text=item["name"],
                font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                fg_color=UI_COLORS["io_point_label"],
                corner_radius=5,
            ).grid(
                row=0,
                column=0,
                sticky="ew",
                padx=UI_PADDING["small"] - 1,
                pady=UI_PADDING["small"] - 1,
            )

            key = next(
                (k for k, v in SEARCH_TYPE_MAP.items() if str(item["type"]) in v),
                None
            )
            if item["type"] == "devOk":
                key = "NDSTAT"
            if key is None:
                key = item["type"]

            ctk.CTkLabel(
                point_frame,
                text = key,
                font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                fg_color=TYPE_COLORS[key],
                width=35,
                corner_radius=5,
            ).grid(
                row=0,
                column=1,
                padx=UI_PADDING["small"] - 1,
                pady=UI_PADDING["small"] - 1,
            )
            row += 1

    @staticmethod
    def _refresh(refresh_type: str) -> None:

        if not Selected.main_frame:
            return

        if refresh_type == "io":
            for widget in Selected.io_frame.winfo_children():
                widget.destroy()
            Selected._create_labels("io")
        elif refresh_type == "vfd":
            for widget in Selected.vfd_frame.winfo_children():
                widget.destroy()
            Selected._create_labels("vfd")
        else:
            for widget in Selected.preset_frame.winfo_children():
                widget.destroy()
            Selected._create_labels("preset")

    @staticmethod
    def clear_selected() -> None:
        """Clears the selected panel"""
        Selected.selected_io_points = []
        Selected.selected_vfd_points = []
        Selected.selected_presets = []
        Selected._refresh("io")
        Selected._refresh("vfd")
        Selected._refresh("preset")

