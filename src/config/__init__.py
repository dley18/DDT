"""
Configuration modules.

This package contains various config
modules for DDT.
"""

from .constants import *
from .point_mapping import *
from .ui_config import *
from .chart_config import *
from .incident_config import *


__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "APP_TITLE",
    "ALARM_CSV_TITLE",
    "ALARM_CSV_HEADERS",
    "DATA_FOLDER_NAME",
    "DATA_FOLDER_HOME",
    "DATA_FOLDER_PATH",
    "BATCH_SIZE",
    "SCREENSIZE",
    "TIME_ZONE_OFFSET_ID",
    "IO_POINTS",
    "VFD_POINTS",
    "IO_TYPES",
    "GRAPH_PRESETS",
    "APP_APPEARANCE",
    "UI_COMPONENTS",
    "COMPONENT_DIMENSIONS",
    "UI_PADDING",
    "UI_FONTS",
    "UI_COLORS",
    "CHART_COLORS",
    "LINE_WIDTH",
    "ASTERICK_SIZE",
    "INCIDENT_TYPE",
    "INCIDENT_STATE",
    "INCIDENT_COLORS",
    "INCIDENT_ARGUMENTS",
    "INCIDENT_ARGUMENTS_V2",
    "INCIDENTS_PER_PAGE",
    "MAGIC_NUMBER",
    "GRAPH_SEARCH_TYPES",
    "MAX_POINTS_PER_SEARCH",
    "SEARCH_TYPE_MAP",
    "TYPE_COLORS",
]
