# FB2 Data Download Tool

FB2 Data Download and Analysis Tool

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Workflow](#workflow)
- [Installation](#installation)
- [Usage](#usage)
- [Development](#development)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Support](#support)
- [Version History](#version-history)


## Overview
An application for processing, analyzing, and visualizing data from FB2 Shearer data dumps.
The tool provides graphing capabilities and an alarm log. 

## Features
- **LZ4 Data import**: Process data from .LZ4 files from FB2 Shearer system

- **File Information**: Double click a file on the homescreen to view information about that file

- **Data Folder**: Creates a directory ~/Documents/DDT (if not found); each time the app is run, it will create a new directory inside that folder that holds the contents of the data analysis

- **Delete Data Folder Contents**: Required to use when processing a second data download within the same instance of the app being run

- **Custom Graphing**: Under Common Points on the Graphing screen, select an unlimited amount of data points to be graphed on the same graph

- **Search Database**: Under Search Database on the Graphing screen, type in any IO Point name and/or filter by any IO Type, and click the add/remove button next to the point to add/remove the point from your current selection

- **Preset Graphing**: Under Preset Graphs on the Graphing screen, select any number of predefined graphs (developer selected data points), to be graphed on separate graphs

- **Selected**: The Selected panel will show you all of the IO/VFD Points and Presets you have selected to graph. The IO Point section will also show you the IO Type of the Point you have selected

- **Parameters**: JNA Current Limit and Cutter Amp Limit Parameters: Enter number to display as a reference line on the graph (Will only show on Haulage or Cutter Amps graphs & custom graphs that contain Haulage Current or Cutter Current points)

- **CSV Generation**: Select the "Generate CSV File with Raw Data" button on the graphing screen to include a CSV file with the selected data during graph generation

- **Incident Viewer**: Page based alarm log sorted by date/time

- **Incident Searching**: 2 search options for alarm log: Search by text (matches text to alarm text and renders only those alarms), and Search by occurrence (Finds first occurrence of the text and highlights it, press ENTER to go to the next occurrence of that text in the alarm log)

- **Help Text**: Click any incident in the alarm log to view help text about what the incident is

- **Report**: A small report on the incident viewer screen that displays the Shearer's serial number and date/time of the data download period

- **Time Zone Offset Detection**: Queries database for time zone offset parameter; if found, applies it to every timestamp, if not, prompts the user with a window to type in a custom offset

- **Status Text and Progress Bar**: Text and Progress bar at the bottom of every screen that shows what is currently happening in the program and how far along it is while doing that process


## Project Structure
```
assets/                          # Images and other dependencies
src/                             # Source code
    config/                      # Configuration files and constants
      chart_config.py            # Bokeh chart configuration model
      constants.py                # Application-wide constants
      incident_config.py         # Incident viewer configurations
      point_mapping.py           # IO, VFD, and Preset Graph definitions
      ui_config.py               # UI configuration presets 
   core/
      application_controller.py  # Main app controller
      workflow_manager.py        # Data processing workflow
   data/
      csv_generator.py           # Handles CSV creation
      database_manager.py        # Database operations
      incident_manager.py        # Incident management
      incident_exporter.py       # Handles exporting alarm log
      selected_data_manager.py   # Handles all USER selected data
   ui/
      components/
         custom_graph.py         # Custom graph UI component
         file_selector.py        # File selector UI component
         incident_viewer.py      # Alarm log UI component
         preset_graph.py         # Preset graph UI component
         search.py               # Search database UI component
         selected.py             # Selected Panel UI component
      screen/
         main_window.py          # Main application window
   util/
      file_util.py               # Various file utilities
      time_util.py               # Various time utilities
      validation.py              # File validation
      util_functions.py          # Shared utility functions
   viz/
      graph_generator.py        # Bokeh graph generation
      plot_point.py              # Manages a single Bokeh plot
   main.py                       # Application entry point
```

## Workflow
1. **File Import**: Users select and import FB2 Shearer data dump files
2. **Database Creation (if not found)**: Extracts the contents from .LZ4 Files and creates one MERGED database from all FB database files.
3. **Graphing Route**: Workflow for graphing proceeds ->
4. **Data point selection**: Users select data points on the graphing screen and select GENERATE when ready
5. **Query**: Data points are queried from the MERGED database and stored in a python Dictionary
6. **Visualization**: Selected points/graphs are shown in the browser after completion of processing
7. **Incident Viewer Route**: Workflow for the incident viewer proceeds ->
8. **Query**: Queries database for all incident ID's and help text
9. **Lookup**: Does a lookup in the extracted .XML file for matching ID's and grabs the corresponding text
10. **Population**: Populates the incident viewer component with all configured incidents
11. **Save Contents**: All important files (plots, CSV, .sqlite database) are saved after creation in 
~/Documents/DDT

## Installation

### Prerequisites
- Python 3.12 or higher
- Windows OS (developed for Windows environment)
- UV package manager

### Setup
1. Clone the repository:
   ```sh
   git clone https://ControlAutomation@dev.azure.com/ControlAutomation/C%20and%20A%20Projects/_git/FB2_DataDownloadTool
   cd FB2_DataDownloadTool
   ```
2. Install dependencies using UV
   ```sh
   uv sync
   ```
3. Run the Application:
   ```sh
   uv run src/main.py
   ```
## Usage
```sh
# Start the application
uv run src/main.py

# Or with Python directly
python src/main.py
```

### Home

#### Home Screen:
 - Click **Add Files** in the bottom left to add your data dump's files - These files will be displayed on the screen
 - Select any of the files on the viewer and click **Remove Selected** to remove them from your selection
 - Click **Clear All** to remove all files from selection
 - To open the Data Folder at any time click the **Open Data Folder** button
 - To clear the contents of the Data Folder click the **Delete Data Folder Contents** button in the bottom right


### Graphing

#### Custom Graph:
 - Select the box next to any points you would like to graph
 - Click **clear** at the bottom to remove any of your selections

#### Search Database:
- Type in any IO Point name in the search box and the panel will render any matches, which you can then click add/remove to add/remove it from you current selection
- Click the **IO Type** dropdown menu to filter for a specific IO Type

#### Preset Graphs:
- Select the box next to any preset graph 
- Again click **clear** at the bottom to remove any of your selections
- Or select **All** in the top left to generate all of the preset graphs

#### Parameters:
- **JNA Current Limit**: Type any number into this field to be displayed as a reference line. Note that this line will only be shown in 2 scenarios - If the user selected the Haulage Amps preset graph or if any of the Haulage Current points have been selected.
- **Cutter Amp Limit**: Type any number into this field to be displayed as a reference line. Note that this line will only be shown in 2 scenarios - If the user selected the Cutter Amps preset graph or if any of the Cutter Current points have been selected.
- **Generate CSV File**: User checks this box to additionally generate a CSV file containing the raw data from graphs/points they selected


### Incident Viewer

#### Incident Pages:
- Incidents will be populated after clicking **Populate**
- After inital incidents have been populated, click **Next** to navigate to the next page, **Previous** to navigate back a page, or **Jump** to enter a page number to jump to 
- Click on any incident in the box to view its **Help Text**
- Click **Export** to export the incident list to a CSV file, that will be opened automatically

#### Searching:
- There is a searchbox above the incidents where users can execute 2 types of seaching
- **Search by text**: When having this radio button selected - Only incidents that have matching text will be displayed
- **Search by occurrence**: When having this radio button selected - All incidents will be shown, and the first occurrence of a match will be highlighted. Click **Enter** on your keyboard to highlight and jump to the next occurrence.

#### Report:
- The Shearer's **Serial Number** and Data Dump's **Time Range** are displayed here

## Development

### Code Style
- **Formatter**: Black
- **Type Hints**: All function signatures include type hints
- **Modular Design**: Clear separation of concerns split into managers and components

## Best Practices
- Use type hints for all function signatures
- Add docstrings for all public methods
- Handle exceptions gracefully with user feedback


## Troubleshooting

### Common Issues
- **Timezone Missing from Data Dump**: Some data dumps will not include a time zone offset parameter, causing the "custom offset" dialog to show often
- **Data Point not Graphed**: This means that the active flag in the Database was set to 0, therefore the point will not be graphed out to the user

## Support
- **Contact**: Dane Ley - dane.ley@global.komatsu

## Version History
- **v1.0**: Initial summer 2024 release with basic functionality and slow processing time
- **v2.0**: Summer 2025 release with improved functionality and processing time
- **v2.1**: Alarm Log export & Date range slider
- **v2.2**: Data Folder Button, Version Info, Adjust CSV Data Formatting to match DPlot, Reference Lines fix, Add time info on Timezone offset prompt
- **v2.3**: Adjusted merging logic to account for multi-schema database files. Implemented a page based incident viewer - fixes issue of rendering a large amount of incidents at one time. Added compatibility for FB209 DB Version 2
- **v3.0**: Added Search Datbase feature, allowing the user to pick any available io-point stored in the database. Added a Selected panel that shows the user what points they have selected. Categorized IO Points by IO Type.

## Author / Developer
- **Dane Ley** - **dane.ley@global.komatsu**

---

*Built for Faceboss 2.0 Data Dumps*
