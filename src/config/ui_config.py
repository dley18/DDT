"""UI configuration presets."""

import customtkinter as ctk

# App theme
APP_APPEARANCE = {
    "appearance_mode": "dark",
    "color_theme": "dark-blue",
    "geometry": "1920x1080",
    "app_icon": "../../assets/images/ddt(invert).ico",
}

# UI logos and elements
UI_COMPONENTS = {
    "joy_faceboss_logo": "../../assets/images/FACEBOSS_20Invert2-removebg-preview.png",
    "faceboss_ddt_logo": "../../assets/images/datadownloadtool-ai-brush-removebg-90tmmxb5.png",
    "ddt_icon": "../../assets/images/ddt.ico",
    "home_btn": "../../assets/images/home.png",
}

COMPONENT_DIMENSIONS = {
    "button": {
        "height": 40,
        "width": 75,
    },
    "label": {},
    "image": {
        "height": 150,
        "width": 600,
    },
    "entry": {"width": 150},
}

UI_PADDING = {
    "small": 5,
    "medium": 10,
    "large": 20,
}

UI_FONTS = {
    "status": 20,
    "label_size": 25,
    "checkbox_size": 15,
}

UI_COLORS = {
    "add": "#009406",
    "add_hover": "#006E06",
    "remove": "#dc3545",
    "remove_hover": "#c82333",
    "clear": "#b00020",
    "clear_hover": "#8e0018",
    "open_data_folder": "#FF5900",
    "open_data_folder_hover": "#CF4E09",
    "delete_database": "#b00020",
    "delete_database_hover": "#8e0018",
    "primary": "#0d6efd",
    "primary_hover": "#0b5ed7",
    "white": "#FFFFFF",
    "black": "#000000",
    "charcoal": "#36454F",
    "charcoal_hover": "#2a353d",
    "checkbox": "#0eeb1d",
    "checkbox_hover": "#11a81b",
    "status": "#EEEEEE",
    "export": "#FF5900",
    "export_hover": "#CF4E09",
    "next": "#0d6efd",
    "next_hover": "#0b5ed7",
    "prev": "#b00020",
    "prev_hover": "#8e0018",
    "jump": "#666666",
    "jump_hover": "#4A4A4A",
    "io_point_label": "#171717", #1C1C1C
    "frame": "#171717",
    "dropdown_btn": "#1C1C1C",
    "dropdown_btn_hover": "#2e2e2e"
}

TYPE_COLORS = {
    "AI": "#038503",
    "AO": "#014701",
    "DI": "#0037ff",
    "DO": "#001a7a",
    "LI": "#fa6a02",
    "LO": "#ad4900",
    "NDSTAT": "#ad02eb",
    "PVI": "#454545",
    "PVO": "#292929",
    "SI": "#fa02b8",
    "SO": "#990070",
    "VFD": "#ff0000",
    "PRESET": "#590613",
}

INCIDENTS_PER_PAGE = 16

MAX_POINTS_PER_SEARCH = 15

GRAPH_SEARCH_TYPES = [
    "All",
    "AI",
    "AO",
    "DI",
    "DO",
    "LI",
    "LO",
    "NDSTAT",
    "PVI",
    "PVO",
    "SI",
    "SO",
]

SEARCH_TYPE_MAP = {
    "AI": ["J_AI_TYPE", "2"],
    "AO": ["J_AO_TYPE", "11"],
    "DI": ["J_DI_TYPE", "0"],
    "DO": ["J_DO_TYPE", "1"],
    "LI": ["J_LI_TYPE", "9"],
    "LO": ["J_LO_TYPE", "10"],
    "NDSTAT": ["J_NDSTAT_TYPE", "12"],
    "PVI": ["J_PVI_TYPE", "3"],
    "PVO": ["J_PVO_TYPE", "4"],
    "SI": ["J_SI_TYPE", "7"],
    "SO": ["J_SO_TYPE", "8"],
}
