"""Main window and application GUI components."""

from PIL import Image

import os
from typing import Callable
import ctypes
import customtkinter as ctk


from config.constants import APP_TITLE, APP_VERSION
from config.ui_config import (
    APP_APPEARANCE,
    COMPONENT_DIMENSIONS,
    UI_COMPONENTS,
    UI_FONTS,
    UI_PADDING,
    UI_COLORS,
)
from ui.components.custom_graph import CustomGraph
from ui.components.file_selector import FileSelector
from ui.components.incident_viewer import IncidentViewer
from ui.components.preset_graph import PresetGraph
from ui.components.search import Search
from ui.components.selected import Selected
from util.file_util import get_path


class MainWindow:
    """Main application window."""

    def __init__(self):
        self.root = None
        self.callbacks = {}
        self.components = {}
        self.setup_window()
        self.create_components()

    def setup_window(self) -> None:
        """Initialize the main window."""

        ctypes.windll.shcore.SetProcessDpiAwareness(1)

        # Load internal shapes/Roboto fonts to use high quality renderer
        ctk_dir = os.path.dirname(ctk.__file__)
        ctk.FontManager.load_font(
            os.path.join(ctk_dir, "assets/fonts/CustomTkinter_shapes_font.otf")
        )

        # Set CustomTkinter theme
        ctk.set_appearance_mode(APP_APPEARANCE["appearance_mode"])
        ctk.set_default_color_theme(APP_APPEARANCE["color_theme"])

        # Create main window
        self.root = ctk.CTk()
        self.root.title(APP_TITLE)
        self.root.geometry(APP_APPEARANCE["geometry"])
        self.root.bind("<Configure>", self.on_window_configure)

        # Set font
        try:
            base = os.path.dirname(os.path.abspath(__file__))
            ctk.FontManager.load_font(
                os.path.join(base, "assets/fonts/Inter-VariableFont_opsz,wght.ttf")
            )
        except Exception as e:
            print(f"Failed to load font: {e}")

        ctk.set_widget_scaling(1)
        ctk.set_window_scaling(1)

        # Set window icon
        try:
            icon_path = get_path(APP_APPEARANCE["app_icon"])
            self.root.iconbitmap(icon_path)
        except:
            pass  # Icon not found, continue without it

        # Configure grid widgets
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def on_window_configure(self, event):
        """Window event handler to re-hide tabs when window resizes."""
        tabview = self.components.get("tabview")
        if not tabview:
            return
        # CTkTabview uses an internal _segmented_button; it may not exist yet on first configure
        btn = getattr(tabview, "_segmented_button", None)
        try:
            if btn and int(btn.winfo_exists()):
                btn.grid_remove()
        except Exception:
            # Ignore spurious Tk errors during layout churn
            pass

    def switch_to_tab(self, tab_name: str) -> None:
        """Switch to a specific tab by name."""
        if "tabview" in self.components:
            tabview = self.components["tabview"]
            tabview.set(tab_name)

    def create_components(self) -> None:
        """Create and layout UI components."""
        # Main container frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)  # Sidebar column
        main_frame.grid_columnconfigure(1, weight=10)  # Content area column

        self.create_header(main_frame)
        self.create_sidebar(main_frame)
        self.create_content_area(main_frame)
        self.create_footer(main_frame)

        # Defer hiding of the tabview segmented button until widgets are realized
        self.root.after_idle(self._hide_tab_header)

    def _hide_tab_header(self) -> None:
        """Hide CTkTabview's segmented button safely when available."""
        tabview = self.components.get("tabview")
        if not tabview:
            return
        btn = getattr(tabview, "_segmented_button", None)
        try:
            if btn and int(btn.winfo_exists()):
                btn.grid_remove()
        except Exception:
            pass

    def create_header(self, parent: ctk.CTkFrame) -> None:
        """Create header section with title and logo."""
        header_frame = ctk.CTkFrame(parent)
        header_frame.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        logo = Image.open(get_path(UI_COMPONENTS["faceboss_ddt_logo"]))
        ctk_logo = ctk.CTkImage(
            light_image=logo,
            dark_image=logo,
            size=(
                COMPONENT_DIMENSIONS["image"]["width"],
                COMPONENT_DIMENSIONS["image"]["height"],
            ),
        )

        logo_label = ctk.CTkLabel(header_frame, text="", image=ctk_logo)
        logo_label.pack(side="top", padx=UI_PADDING["small"], pady=UI_PADDING["small"])

        self.components["header"] = header_frame

    def create_sidebar(self, parent: ctk.CTkFrame) -> None:
        """Create sidebar for app navigation."""

        # Side bar panel
        side_bar_frame = ctk.CTkFrame(parent)
        side_bar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")

        side_bar_frame.grid_columnconfigure(0, weight=1)
        side_bar_frame.grid_rowconfigure(0, weight=0)
        side_bar_frame.grid_rowconfigure(1, weight=1)
        side_bar_frame.grid_rowconfigure(2, weight=1)
        side_bar_frame.grid_rowconfigure(3, weight=0)
        side_bar_frame.grid_rowconfigure(4, weight=1)
        side_bar_frame.grid_rowconfigure(5, weight=0)
        side_bar_frame.grid_rowconfigure(6, weight=1)

        # App version number
        version_label = ctk.CTkLabel(
            side_bar_frame, 
            text=APP_VERSION,
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
        )
        version_label.grid(row=0, column=0, sticky="w", padx=UI_PADDING["small"])

        # App logo
        logo = Image.open(get_path(UI_COMPONENTS["ddt_icon"]))
        ctk_logo = ctk.CTkImage(
            light_image=logo,
            dark_image=logo,
            size=(
                200,
                200,
            ),
        )
        logo_label = ctk.CTkLabel(side_bar_frame, text="", image=ctk_logo)
        logo_label.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Home button
        home_btn = ctk.CTkButton(
            side_bar_frame,
            text="Home",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            command=lambda: self.switch_to_tab("File Selection"),
            fg_color="transparent",
            hover_color=UI_COLORS["charcoal_hover"],
            corner_radius=0,
        )
        home_btn.grid(
            row=2,
            column=0,
            sticky="nsew",
        )

        # Frame seperator 1
        seperator_frame1 = ctk.CTkFrame(
            side_bar_frame, height=2, fg_color=UI_COLORS["black"]
        )
        seperator_frame1.grid(row=3, column=0, sticky="ew", padx=UI_PADDING["small"])

        # Graphing button
        graphing_btn = ctk.CTkButton(
            side_bar_frame,
            text="Graphing",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            command=lambda: self.switch_to_tab("Graphing"),
            fg_color="transparent",
            hover_color=UI_COLORS["charcoal_hover"],
            corner_radius=0,
        )
        graphing_btn.grid(
            row=4,
            column=0,
            sticky="nsew",
        )

        # Frame seperator 2
        seperator_frame2 = ctk.CTkFrame(
            side_bar_frame, height=2, fg_color=UI_COLORS["black"]
        )
        seperator_frame2.grid(row=5, column=0, sticky="ew", padx=UI_PADDING["small"])

        # Incident button
        incident_btn = ctk.CTkButton(
            side_bar_frame,
            text="Incident Viewer",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            command=lambda: self.switch_to_tab("Incident Viewer"),
            fg_color="transparent",
            hover_color=UI_COLORS["charcoal_hover"],
            corner_radius=0,
        )
        incident_btn.grid(
            row=6,
            column=0,
            sticky="nsew",
        )

    def create_content_area(self, parent: ctk.CTkFrame) -> None:
        """Create main content area with tabbed interface."""
        # Create tabview
        tabview = ctk.CTkTabview(
            parent,
            fg_color="transparent",
        )
        tabview.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # File selection Tab
        file_tab = tabview.add("File Selection")
        self.create_file_selection_tab(file_tab)

        # Grahping tab
        graphing_tab = tabview.add("Graphing")
        self.create_graphing_tab(graphing_tab)

        # Incident viewer tab
        incident_tab = tabview.add("Incident Viewer")
        self.create_incident_viewer_tab(incident_tab)

        # Hide tabs
        # tabview._segmented_button.grid_remove()
        tabview.grid_propagate(False)
        tabview.configure(width=1200, height=700)
        self.components["tabview"] = tabview

    def create_file_selection_tab(self, parent: ctk.CTkFrame) -> None:
        """Create file selection interface."""
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Instructions
        instructions_label = ctk.CTkLabel(
            parent,
            text="Data Download Files:",
            font=ctk.CTkFont(family="Inter", size=32, weight="bold"),
            text_color=UI_COLORS["white"],
        )
        instructions_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # File selector component
        file_selector = FileSelector(parent)
        file_selector.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Buttons frame
        buttons_frame = ctk.CTkFrame(parent)
        buttons_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Add files button
        add_files_btn = ctk.CTkButton(
            buttons_frame,
            text="➕ Add Files",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            width=COMPONENT_DIMENSIONS["button"]["width"],
            height=COMPONENT_DIMENSIONS["button"]["height"],
            command=lambda: file_selector.add_files(),
            fg_color=UI_COLORS["add"],
            hover_color=UI_COLORS["add_hover"],
            text_color=UI_COLORS["white"],
            corner_radius=8,
        )
        add_files_btn.pack(
            side="left", padx=UI_PADDING["small"], pady=UI_PADDING["small"]
        )
        file_selector.set_callback("files_added", self.handle_files_added)

        # Remove files button
        remove_files_btn = ctk.CTkButton(
            buttons_frame,
            text="Remove Selected",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            width=COMPONENT_DIMENSIONS["button"]["width"],
            height=COMPONENT_DIMENSIONS["button"]["height"],
            command=lambda: file_selector.remove_selected_files(),
            fg_color=UI_COLORS["remove"],
            hover_color=UI_COLORS["remove_hover"],
            text_color=UI_COLORS["white"],
            corner_radius=8,
        )
        remove_files_btn.pack(
            side="left", padx=UI_PADDING["small"], pady=UI_PADDING["small"]
        )
        file_selector.set_callback("files_removed", self.handle_files_removed)

        # Clear all button
        clear_all_btn = ctk.CTkButton(
            buttons_frame,
            text="Clear All",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            width=COMPONENT_DIMENSIONS["button"]["width"],
            height=COMPONENT_DIMENSIONS["button"]["height"],
            command=lambda: file_selector.clear_all_files(),
            fg_color=UI_COLORS["clear"],
            hover_color=UI_COLORS["clear_hover"],
            text_color=UI_COLORS["white"],
            corner_radius=8,
        )
        clear_all_btn.pack(
            side="left", padx=UI_PADDING["small"], pady=UI_PADDING["small"]
        )
        file_selector.set_callback("files_cleared", self.handle_files_cleared)

        # Delete database file button
        delete_database_file_btn = ctk.CTkButton(
            buttons_frame,
            text="Delete Data Folder Contents",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            width=COMPONENT_DIMENSIONS["button"]["width"] * 3.5,
            height=COMPONENT_DIMENSIONS["button"]["height"] * 1.5,
            command=lambda: file_selector.delete_database_file(),
            fg_color=UI_COLORS["delete_database"],
            hover_color=UI_COLORS["delete_database_hover"],
            text_color=UI_COLORS["white"],
            corner_radius=8,
        )
        delete_database_file_btn.pack(
            side="right", padx=UI_PADDING["small"], pady=UI_PADDING["small"]
        )
        file_selector.set_callback("database_closing", self.handle_database_closing)
        file_selector.set_callback("database_deleted", self.handle_database_deleted)

        # Open data folder button
        open_data_folder_btn = ctk.CTkButton(
            buttons_frame, 
            text="Open Data Folder",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            width=COMPONENT_DIMENSIONS["button"]["width"] * 3.5,
            height=COMPONENT_DIMENSIONS["button"]["height"] * 1.5,
            command=lambda: file_selector.open_data_folder(),
            fg_color=UI_COLORS["open_data_folder"],
            hover_color=UI_COLORS["open_data_folder_hover"],
            text_color=UI_COLORS["white"],
            corner_radius=8,
        )
        open_data_folder_btn.pack(
            side="right", padx=UI_PADDING["small"], pady=UI_PADDING["small"]
        )
        file_selector.set_callback("data_folder_opened", self.handle_data_folder_opened)

        self.components["file_selector"] = file_selector
        self.components["file_buttons"] = {
            "add": add_files_btn,
            "remove": remove_files_btn,
            "clear": clear_all_btn,
            "open_data_folder": open_data_folder_btn,
            "delete_database": delete_database_file_btn,
        }

    def create_graphing_tab(self, parent: ctk.CTkFrame) -> None:
        """Create graphing interface."""
        parent.grid_rowconfigure(0, weight=1)

        parent.grid_columnconfigure(0, weight=5, uniform="columns")
        parent.grid_columnconfigure(1, weight=5, uniform="columns")
        parent.grid_columnconfigure(2, weight=2)
        parent.grid_columnconfigure(3, weight=1)

        # Custom graph panel
        custom_graph_frame = ctk.CTkFrame(parent)
        custom_graph_frame.grid(
            row=0,
            column=0,
            rowspan=2,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )
        custom_graph_frame.grid_rowconfigure(1, weight=1)
        custom_graph_frame.grid_columnconfigure(0, weight=1)

        # Custom graph label
        custom_graph_label = ctk.CTkLabel(
            custom_graph_frame,
            text="Common Points",
            font=ctk.CTkFont(family="Inter", size=32, weight="bold"),
            text_color=UI_COLORS["white"],
        )
        custom_graph_label.grid(
            row=0,
            column=0,
            sticky="n",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Custom graph component
        custom_graph = CustomGraph(custom_graph_frame)
        custom_graph.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Clear button for custom graph
        clear_custom_graph_btn = ctk.CTkButton(
            custom_graph_frame,
            text="Clear",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            fg_color=UI_COLORS["clear"],
            hover_color=UI_COLORS["clear_hover"],
            text_color=UI_COLORS["white"],
            corner_radius=8,
            command=lambda: custom_graph.clear(),
        )
        clear_custom_graph_btn.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )
        custom_graph.set_callback(
            "cleared_custom_points", self.handle_cleared_custom_points
        )

        # Search Panel
        search_frame = ctk.CTkFrame(parent)
        search_frame.grid(
            row=0,
            column=1,
            rowspan=2,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )
        search_frame.grid_rowconfigure(1, weight=1)
        search_frame.grid_columnconfigure(0, weight=1)

        # Search label
        search_label = ctk.CTkLabel(
            search_frame,
            text="Search Database",
            font=ctk.CTkFont(family="Inter", size=32, weight="bold"),
            text_color=UI_COLORS["white"],
        )
        search_label.grid(
            row=0,
            column=0,
            sticky="n",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        search_component = Search(search_frame)
        search_component.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Preset graph panel
        preset_graph_frame = ctk.CTkFrame(parent)
        preset_graph_frame.grid(
            row=0,
            column=2,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )
        preset_graph_frame.grid_rowconfigure(1, weight=1)
        preset_graph_frame.grid_columnconfigure(0, weight=1)

        # Preset graph label
        preset_graph_label = ctk.CTkLabel(
            preset_graph_frame,
            text="Presets",
            font=ctk.CTkFont(family="Inter", size=32, weight="bold"),
            text_color=UI_COLORS["white"],
        )
        preset_graph_label.grid(
            row=0,
            column=0,
            sticky="n",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Preset graph component
        preset_graph = PresetGraph(preset_graph_frame)
        preset_graph.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Clear preset graph selection button
        clear_preset_graph_btn = ctk.CTkButton(
            preset_graph_frame,
            text="Clear",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            fg_color=UI_COLORS["clear"],
            hover_color=UI_COLORS["clear_hover"],
            text_color=UI_COLORS["white"],
            corner_radius=8,
            command=lambda: preset_graph.clear(),
        )
        clear_preset_graph_btn.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )
        preset_graph.set_callback(
            "cleared_graph_presets", self.handle_cleared_graph_presets
        )

        # Selected Panel
        selected_frame = ctk.CTkFrame(parent)
        selected_frame.grid(
            row=1,
            column=2,
            columnspan=2,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )
        selected_frame.grid_rowconfigure(1, weight=1)
        selected_frame.grid_columnconfigure(0, weight=1)

        selected_label = ctk.CTkLabel(
            selected_frame,
            text="Selected",
            font=ctk.CTkFont(family="Inter", size=32, weight="bold"),
            text_color=UI_COLORS["white"]
        )
        selected_label.grid(
            row=0,
            column=0,
            sticky="n",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        selected_component = Selected(selected_frame)
        selected_component.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Parameters panel
        parameters_frame = ctk.CTkFrame(parent)
        parameters_frame.grid(
            row=0,
            column=3,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )
        parameters_frame.grid_rowconfigure(6, weight=1)
        parameters_frame.grid_columnconfigure(0, weight=1)

        # Parameters label
        parameters_label = ctk.CTkLabel(
            parameters_frame,
            text="Parameters",
            font=ctk.CTkFont(family="Inter", size=32, weight="bold"),
            text_color=UI_COLORS["white"],
        )
        parameters_label.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"] * 2,
        )

        # JNA current limit label
        jna_current_limit_label = ctk.CTkLabel(
            parameters_frame,
            text="JNA Current Limit:",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color=UI_COLORS["white"],
        )
        jna_current_limit_label.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # JNA current limit entry
        jna_current_limit_var = ctk.StringVar()
        jna_current_limit_entry = ctk.CTkEntry(
            parameters_frame,
            textvariable=jna_current_limit_var,
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color=UI_COLORS["white"],
        )
        jna_current_limit_entry.grid(
            row=2,
            column=0,
            padx=UI_PADDING["small"] * 3,
            pady=(0, UI_PADDING["small"] * 3),
        )

        # Cutter amp limit label
        cutter_amp_limit_label = ctk.CTkLabel(
            parameters_frame,
            text="Cutter Amp Limit:",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color=UI_COLORS["white"],
        )
        cutter_amp_limit_label.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Cutter amp limit entry
        cutter_amp_limit_var = ctk.StringVar()
        cutter_amp_limit_entry = ctk.CTkEntry(
            parameters_frame,
            textvariable=cutter_amp_limit_var,
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color=UI_COLORS["white"],
        )
        cutter_amp_limit_entry.grid(
            row=4,
            column=0,
            padx=UI_PADDING["small"] * 3,
            pady=(0, UI_PADDING["small"] * 3),
        )

        # Include CSV option checkbox
        include_csv_var = ctk.StringVar(value="off")
        include_csv_checkbox = ctk.CTkCheckBox(
            parameters_frame,
            text="Generate CSV File",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            width=36,
            height=36,
            checkbox_width=32,
            checkbox_height=32,
            variable=include_csv_var,
            onvalue="on",
            offvalue="off",
            fg_color=UI_COLORS["checkbox"],
            hover_color=UI_COLORS["checkbox_hover"],
            corner_radius=3,
            border_width=1,
            text_color=UI_COLORS["white"],
        )
        include_csv_checkbox.grid(
            row=5,
            column=0,
            padx=UI_PADDING["small"] * 3,
            pady=UI_PADDING["small"] * 3,
        )

        # Graph button
        generate_btn = ctk.CTkButton(
            parameters_frame,
            text="Generate",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            width=300,
            height=125,
            fg_color=UI_COLORS["primary"],
            hover_color=UI_COLORS["primary_hover"],
            text_color=UI_COLORS["white"],
            corner_radius=8,
            command=lambda: self.on_generate_clicked(),
        )
        generate_btn.grid(
            row=6,
            column=0,
            padx=UI_PADDING["small"] * 5,
            pady=(UI_PADDING["small"] * 10, UI_PADDING["small"] * 5),
        )

        self.components["graphing"] = {
            "custom_graph": {
                "component": custom_graph,
                "frame": custom_graph_frame,
                "label": custom_graph_label,
                "clear_btn": clear_custom_graph_btn,
            },
            "search_panel": {
                    "component": search_component,
                    "frame": search_frame,
                    "label": search_label,
            },
            "preset_graph": {
                "component": preset_graph,
                "frame": preset_graph_frame,
                "label": preset_graph_label,
                "clear_btn": clear_preset_graph_btn,
            },
            "selected_panel": {
                    "component": selected_component,
                    "frame": selected_frame,
                    "label": selected_label,
            },
            "parameters": {
                "jna_current_limit": jna_current_limit_entry,
                "jna_current_limit_var": jna_current_limit_var,
                "cutter_amp_limit": cutter_amp_limit_entry,
                "cutter_amp_limit_var": cutter_amp_limit_var,
                "include_csv_checkbox": include_csv_checkbox,
                "include_csv_var": include_csv_var,
            },
            "generate": generate_btn,
        }

    def create_incident_viewer_tab(self, parent: ctk.CTkFrame) -> None:
        """Create incident viewer interface."""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=10)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(2, weight=1)

        # Incident viewer panel
        incident_viewer_frame = ctk.CTkFrame(parent)
        incident_viewer_frame.grid(
            row=0,
            column=0,
            rowspan=2,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        incident_viewer_frame.grid_rowconfigure(1, weight=1)
        incident_viewer_frame.grid_columnconfigure(0, weight=1)

        # Incident viewer label
        incident_viewer_label = ctk.CTkLabel(
            incident_viewer_frame,
            text="Incident Viewer",
            font=ctk.CTkFont(family="Inter", size=32, weight="bold"),
            text_color=UI_COLORS["white"],
        )
        incident_viewer_label.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Incident viewer component
        incident_viewer = IncidentViewer(incident_viewer_frame)
        incident_viewer.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Incident viewer options panel
        incident_viewer_options_frame = ctk.CTkFrame(parent)
        incident_viewer_options_frame.grid(
            row=0,
            column=1,
            rowspan=2,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Text search option
        search_type_var = ctk.StringVar(value="text")
        text_search_radio_btn = ctk.CTkRadioButton(
            incident_viewer_options_frame,
            text="Search by text",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            radiobutton_width=36,
            radiobutton_height=36,
            border_color="#565F6E",
            hover_color="#788291",
            fg_color=UI_COLORS["white"],
            border_width_unchecked=2,
            border_width_checked=5,
            corner_radius=50,
            text_color=UI_COLORS["white"],
            variable=search_type_var,
            value="text",
            command=self.on_text_search_selected,
        )
        text_search_radio_btn.grid(
            row=0,
            column=0,
            sticky="w",
            padx=UI_PADDING["small"] * 2,
            pady=(UI_PADDING["small"] * 10, UI_PADDING["small"]),
        )

        # Occurence search option
        occurrence_search_radio_btn = ctk.CTkRadioButton(
            incident_viewer_options_frame,
            text="Search by occurrence",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            radiobutton_width=36,
            radiobutton_height=36,
            border_color="#565F6E",
            hover_color="#788291",
            fg_color=UI_COLORS["white"],
            border_width_unchecked=2,
            border_width_checked=5,
            corner_radius=50,
            text_color=UI_COLORS["white"],
            variable=search_type_var,
            value="occurrence",
            command=self.on_occurrence_search_selected,
        )
        occurrence_search_radio_btn.grid(
            row=1,
            column=0,
            sticky="w",
            padx=UI_PADDING["small"] * 2,
            pady=UI_PADDING["small"],
        )

        # Populate incident viewer button
        populate_btn = ctk.CTkButton(
            incident_viewer_options_frame,
            text="Populate",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            width=250,
            height=90,
            fg_color=UI_COLORS["primary"],
            hover_color=UI_COLORS["primary_hover"],
            text_color=UI_COLORS["white"],
            corner_radius=8,
            command=lambda: self.on_populate_incident_viewer(),
        )
        populate_btn.grid(
            row=2,
            column=0,
            sticky="sw",
            padx=UI_PADDING["small"],
            pady=(UI_PADDING["small"] * 25, UI_PADDING["small"]),
        )

        # Export incidents to csv button
        export_btn = ctk.CTkButton(
            incident_viewer_options_frame,
            text="Export",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            width=250,
            height=90,
            fg_color=UI_COLORS["export"],
            hover_color=UI_COLORS["export_hover"],
            text_color=UI_COLORS["white"],
            corner_radius=8,
            command=lambda: self.on_export_incidents(),
        )
        export_btn.grid(
            row=3,
            column=0,
            sticky="sw",
            padx=UI_PADDING["small"],
            pady=(UI_PADDING["small"] * 25, UI_PADDING["small"]),
        )
        export_btn.configure(state="disabled")

        # Report panel
        report_frame = ctk.CTkFrame(parent)
        report_frame.grid(
            row=0,
            column=2,
            sticky="nsew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )
        report_frame.grid_rowconfigure(1, weight=1)
        report_frame.grid_rowconfigure(2, weight=0)
        report_frame.grid_rowconfigure(3, weight=1)
        report_frame.grid_rowconfigure(4, weight=0)
        report_frame.grid_rowconfigure(5, weight=1)

        # Report label
        report_label = ctk.CTkLabel(
            report_frame,
            text="Report",
            font=ctk.CTkFont(family="Inter", size=32, weight="bold"),
        )
        report_label.grid(
            row=0, column=0, padx=UI_PADDING["small"], pady=UI_PADDING["small"]
        )

        # Serial number label
        serial_number_label = ctk.CTkLabel(
            report_frame,
            text="Serial Number: LWS###",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
        )
        serial_number_label.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Frame seperator 1
        seperator_frame1 = ctk.CTkFrame(
            report_frame, height=2, fg_color=UI_COLORS["white"]
        )
        seperator_frame1.grid(row=2, column=0, sticky="ew", padx=UI_PADDING["small"])

        # Date label
        date_label = ctk.CTkLabel(
            report_frame,
            text="Date: **/**/** - **/**/**",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
        )
        date_label.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Frame seperator 2
        seperator_frame2 = ctk.CTkFrame(
            report_frame, height=2, fg_color=UI_COLORS["white"]
        )
        seperator_frame2.grid(row=4, column=0, sticky="ew", padx=UI_PADDING["small"])

        # Time label
        time_label = ctk.CTkLabel(
            report_frame,
            text="Time: 00:00:00 - 00:00:00",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
        )
        time_label.grid(
            row=5,
            column=0,
            sticky="ew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        self.components["incident"] = {
            "incident_viewer": {
                "component": incident_viewer,
                "frame": incident_viewer_frame,
                "label": incident_viewer_label,
            },
            "incident_viewer_options": {
                "search_type_var": search_type_var,
                "text_search_radio_btn": text_search_radio_btn,
                "occurrence_search_btn": occurrence_search_radio_btn,
                "populate": populate_btn,
                "export": export_btn,
            },
            "report": {
                "serial_number": serial_number_label,
                "date": date_label,
                "time": time_label,
            },
        }

    def create_footer(self, parent: ctk.CTkFrame) -> None:
        """Create footer with status bar."""
        footer_frame = ctk.CTkFrame(parent)
        footer_frame.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )

        # Status label
        status_label = ctk.CTkLabel(
            footer_frame,
            text="Ready",
            font=ctk.CTkFont(size=UI_FONTS["status"]),
            text_color=UI_COLORS["status"],
        )
        status_label.pack(
            side="left", padx=UI_PADDING["small"], pady=UI_PADDING["small"]
        )

        # Progress bar
        progress_bar = ctk.CTkProgressBar(
            footer_frame,
            width=800,
            height=30,
            fg_color=UI_COLORS["frame"],
            progress_color=UI_COLORS["primary"],
            corner_radius=8,
        )
        progress_bar.pack(
            side="right",
            padx=UI_PADDING["small"],
            pady=UI_PADDING["small"],
        )
        progress_bar.set(0)

        self.components["footer"] = {"status": status_label, "progress": progress_bar}

    def on_text_search_selected(self):
        """Set search mode to text."""
        incident_viewer = self.components["incident"]["incident_viewer"]["component"]
        incident_viewer.set_search_mode("text")

    def on_occurrence_search_selected(self):
        """Set search mode to occurrence."""
        incident_viewer = self.components["incident"]["incident_viewer"]["component"]
        incident_viewer.set_search_mode("occurrence")

    def set_callback(self, event_name: str, callback: Callable) -> None:
        """
        Set callback function for UI events.

        Parameters:
          event_name (str): Name of the event
          callback (Callable): Callback function
        """
        self.callbacks[event_name] = callback

    def handle_files_added(self, count: int) -> None:
        """Handles files added to file selector component"""
        # Update UI
        self.update_status(f"Added {count} files")
        self.disable_graphing_btns()
        self.disable_incident_btns()
        params = self.collect_files_added_parameters()

        # Notify controller
        if "files_added" in self.callbacks:
            self.callbacks["files_added"](count, params)

    def handle_files_removed(self, count: int) -> None:
        """Handle files removed from file selector."""
        # Update UI
        self.update_status(f"Removed {count} files")

        # Notify controller
        if "files_removed" in self.callbacks:
            self.callbacks["files_removed"](count)

    def handle_files_cleared(self, count: int) -> None:
        """Handles files cleared from file selector."""
        # Update UI
        self.update_status(f"Removed {count} files")

        # Notify controller
        if "files_cleared" in self.callbacks:
            self.callbacks["files_cleared"](count)

    def handle_data_folder_opened(self) -> None:
        """Handles request to open data folder."""
        # Update UI
        self.update_status("Data folder opened")

        # Notify controller
        if "data_folder_opened" in self.callbacks:
            self.callbacks["data_folder_opened"]()

    def handle_cleared_custom_points(self, count: int) -> None:
        """Handles points cleared from custom graph."""
        # Update UI
        self.update_status(f"Cleared {count} points")

        # Notify controller
        if "cleared_custom_points" in self.callbacks:
            self.callbacks["cleared_custom_points"](count)

    def handle_cleared_graph_presets(self, count: int) -> None:
        """Handles presets cleared from selection."""
        # Update UI
        self.update_status(f"Cleared {count} presets")

        # Notify controller
        if "cleared_graph_presets" in self.callbacks:
            self.callbacks["cleared_graph_presets"](count)

    def handle_database_closing(self) -> None:
        """Handle request to close database connections before deletion."""

        self.update_status("Closing database connections...")
        self.update_progress(0.2)

        # Notify controller to close connections
        if "close_database_connections" in self.callbacks:
            self.callbacks["close_database_connections"]()

    def handle_database_deleted(self) -> None:
        """Handles deletion of merged database file."""

        # Update UI
        self.update_status("Data folder contents deleted successfully.")
        self.update_progress(1.0)

        # Clear the incident viewer
        incident_viewer = self.components["incident"]["incident_viewer"]["component"]
        incident_viewer.clear_incidents()
        incident_viewer.reset_page_number()
        self.components["file_selector"].clear_all_files(force=True)

        self.components["incident"]["report"]["serial_number"].configure(
            text="Serial Number: LWS###"
        )
        self.components["incident"]["report"]["date"].configure(
            text="Date: **/**/** - **/**/**"
        )
        self.components["incident"]["report"]["time"].configure(
            text="Time: 00:00:00 - 00:00:00"
        )

        # Enable button click
        self.components["incident"]["incident_viewer_options"]["populate"].configure(
            state="disabled"
        )

        self.components["incident"]["incident_viewer_options"]["export"].configure(
            state="disabled"
        )

        self.components["graphing"]["search_panel"]["component"].clear_component()
        self.components["graphing"]["custom_graph"]["component"].clear()
        self.components["graphing"]["preset_graph"]["component"].clear()
        Selected.clear_selected()

        # Reset progress bar after a delay
        self.root.after(2000, lambda: self.update_progress(0))

        # Notify controller
        if "database_deleted" in self.callbacks:
            self.callbacks["database_deleted"]()

    def collect_files_added_parameters(self) -> dict:
        """
        Collect all parameters needed after adding files
        to the File Selector.

        Returns:
            dict: Dictionary containing all file loading parameters.
        """
        selected_files = self.components["file_selector"].get_selected_files()

        return {
            "files": selected_files,
            "search_panel": self.components["graphing"]["search_panel"]["component"]
        }


    def collect_generation_parameters(self) -> dict:
        """
        Collect all parameters needed for graph generation.

        Returns:
            dict: Dictionary containing all graphing parameters.
        """
        graphing_components = self.components["graphing"]

        # Get selected custom points
        custom_graph = graphing_components["custom_graph"]["component"]
        selected_io_points = Selected.selected_io_points
        selected_vfd_points = [entry["name"] for entry in Selected.selected_vfd_points]

        # Get selected preset graphs
        preset_graph = graphing_components["preset_graph"]["component"]
        selected_presets = [entry["name"] for entry in Selected.selected_presets]

        # Get paramter values
        params = graphing_components["parameters"]
        jna_limit = params["jna_current_limit_var"].get() or ""
        cutter_limit = params["cutter_amp_limit_var"].get() or ""
        include_csv = params["include_csv_var"].get() == "on"

        # Get selected files
        selected_files = self.components["file_selector"].get_selected_files()

        return {
            "files": selected_files,
            "io_points": selected_io_points,
            "vfd_points": selected_vfd_points,
            "preset_graphs": selected_presets,
            "jna_current_limit": jna_limit,
            "cutter_amp_limit": cutter_limit,
            "include_csv": include_csv,
        }

    def collect_report_parameters(self) -> dict:
        """
        Collect all parameters needed for report population.

        Returns:
            dict: Dictionary containing all of the report parameters.
        """

        serial_num_label = self.components["incident"]["report"]["serial_number"]
        date_label = self.components["incident"]["report"]["date"]
        time_label = self.components["incident"]["report"]["time"]

        return {"serial_num": serial_num_label, "date": date_label, "time": time_label}

    def collect_incident_parameters(self) -> dict:
        """
        Collect all parameters needed for incident population.

        Returns:
            dict: Dictionary containing all of the incident parameters.
        """

        selected_files = self.components["file_selector"].get_selected_files()
        incident_viewer = self.components["incident"]["incident_viewer"]["component"]
        export_button = self.components["incident"]["incident_viewer_options"]["export"]

        return {"files": selected_files, "incident_viewer": incident_viewer, "export_button": export_button}

    def on_generate_clicked(self) -> None:
        """Handle generate button click."""

        # Collect parameters
        params = self.collect_generation_parameters()

        # Update UI
        self.update_status("Starting graph generation...")
        self.update_progress(0.1)

        self.disable_graphing_btns()

        # Notify controller
        if "generate_graphs" in self.callbacks:
            self.callbacks["generate_graphs"](params)

    def on_populate_incident_viewer(self) -> None:
        """Handle populate incident viewer button click."""
        try:

            incident_params = self.collect_incident_parameters()
            report_params = self.collect_report_parameters()

            # Update UI
            self.update_status("Populating incident viewer...")
            self.update_progress(0.1)

            self.disable_incident_btns()

            # Notify controller
            if "populate_incidents" in self.callbacks:
                self.callbacks["populate_incidents"](incident_params)

            if "populate_report" in self.callbacks:
                self.callbacks["populate_report"](report_params)

        except Exception as e:
            self.update_status(f"Error starting incident population: {e}")

    def on_export_incidents(self) -> None:
        """Handle export alarms button click."""
        try:
            self.update_status("Exporting incidents to a csv file...")
            self.update_progress(0.1)

            if "export_incidents" in self.callbacks:
                self.callbacks["export_incidents"]()

        except Exception as e:
            self.update_status(f"Error exporting incidents: {e}")

    def disable_incident_btns(self):

        self.components["incident"]["incident_viewer_options"][
            "populate"
        ].configure(state="disabled")

    def disable_graphing_btns(self):
        # Disable button clicks
        self.components["graphing"]["generate"].configure(state="disabled")
        self.components["graphing"]["custom_graph"]["clear_btn"].configure(
            state="disabled"
        )
        self.components["graphing"]["preset_graph"]["clear_btn"].configure(
            state="disabled"
        )
        self.components["graphing"]["parameters"]["jna_current_limit"].configure(
            state="disabled"
        )
        self.components["graphing"]["parameters"]["cutter_amp_limit"].configure(
            state="disabled"
        )
        self.components["graphing"]["parameters"]["include_csv_checkbox"].configure(
            state="disabled"
        )
        self.components["graphing"]["custom_graph"]["component"].disable_checkboxes()
        self.components["graphing"]["preset_graph"]["component"].disable_checkboxes()

    def enable_graphing_btns(self):
        """Re-enable the generate button."""
        self.components["graphing"]["generate"].configure(state="normal")
        self.components["graphing"]["custom_graph"]["clear_btn"].configure(
            state="normal"
        )
        self.components["graphing"]["preset_graph"]["clear_btn"].configure(
            state="normal"
        )
        self.components["graphing"]["parameters"]["jna_current_limit"].configure(
            state="normal"
        )
        self.components["graphing"]["parameters"]["cutter_amp_limit"].configure(
            state="normal"
        )
        self.components["graphing"]["parameters"]["include_csv_checkbox"].configure(
            state="normal"
        )
        self.components["graphing"]["custom_graph"]["component"].enable_checkboxes()
        self.components["graphing"]["preset_graph"]["component"].enable_checkboxes()

    def enable_incident_population(self):
        """Re-enable the populate button."""
        self.components["incident"]["incident_viewer_options"][
                "populate"
            ].configure(state="normal")

    def enable_database_deletion(self):
        """Enable the database deletion button."""
        self.components["file_buttons"]["delete_database"].configure(state="normal")

    def disable_database_deletion(self):
        """Disable database deletion button."""
        self.components["file_buttons"]["delete_database"].configure(state="disabled")

    def update_status(self, message: str) -> None:
        """
        Update status message.

        Parameters:
            message (str): Status message to display
        """
        if "footer" in self.components:
            self.components["footer"]["status"].configure(text=message)

    def update_progress(self, value: float) -> None:
        """
        Update progress bar.

        Parameters:
            value (float): Progress value between 0 and 1
        """
        if "footer" in self.components:
            self.components["footer"]["progress"].set(value)

    def run(self):
        """Run mainloop of GUI."""
        self.root.mainloop()
