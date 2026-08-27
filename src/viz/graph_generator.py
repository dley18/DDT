"""Bokeh graph generation module."""

from typing import Dict, List
import datetime
import os

from bokeh.plotting import figure, output_file, save
from bokeh.models import (
    HoverTool,
    DatetimeTickFormatter,
    CustomJSHover,
    CustomJS,
    Div,
    Button,
    CheckboxGroup,
    Span,
    Label,
    DatetimeRangeSlider
)
from bokeh.layouts import column, row
from bokeh.io import curdoc
import numpy as np
from bs4 import BeautifulSoup

from config.chart_config import CHART_COLORS
from config.constants import DATA_FOLDER_PATH, SCREENSIZE
from viz.plot_point import PlotPoint
from util import find_min_max_time


class GraphGenerator:
    """Generator for Bokeh graphs."""

    def __init__(self, data: dict, jna_limit: str, cutter_limit: str):
        self.data = data["preset"]
        self.jna_limit = (
            int(jna_limit) if jna_limit != "" and jna_limit.isnumeric() else None
        )
        self.cutter_limit = (
            int(cutter_limit)
            if cutter_limit != "" and cutter_limit.isnumeric()
            else None
        )

        # Unpack io and vfd points from dictionary
        combined = {**data.get("io", {}), **data.get("vfd", {})}
        if combined:
            self.data["Custom"] = combined

        # Dark theme
        curdoc().theme = "dark_minimal"

        # Layout components
        self.custom_css = None
        self.custom_css_div = None
        self.checkboxes = None
        self.toggle_symbols_btn = None
        self.date_range_slider = None

    def generate_plots(self):
        """Generate all graphs."""

        # Create a single plot for every preset
        for graph_name, graph_data in self.data.items():
            self._create_single_plot(graph_name, graph_data)

    def _create_single_plot(
        self, plot_name: str, plot_data: Dict[str, List[Dict]]
    ) -> bool:
        """
        Create a bokeh plot.

        Parameters:
            plot_name (str): Name of the plot
            plot_data (dict): Data to plot

        Returns:
            bool: True if plot generation succesful, False otherwise
        """

        # Line & asterick renderers dict
        renderers = {}
        renderers["line"] = {}
        renderers["asterick"] = {}

        # Create bokeh figure
        plot = figure(
            title=plot_name,
            x_axis_label="Time",
            y_axis_label="Value",
            x_axis_type="datetime",
            width=SCREENSIZE[0],
            height=SCREENSIZE[1],
        )

        min_date, max_date = find_min_max_time(plot_data)

        self.date_range_slider = DatetimeRangeSlider(
            value=(min_date, max_date),
            start=min_date,
            end=max_date,
            step=60_000, # One minute
            title="Date Range",
            bar_color="black",
            tooltips=True,
        )

        # Callback updates the plot x_range
        self.date_range_slider.js_on_change(
            "value",
            CustomJS(
                args=dict(x_range=plot.x_range),
                code="""
                    // cb_obj.value is [start_ms, end_ms] (numbers)
                    const v = cb_obj.value;
                    x_range.start = v[0];
                    x_range.end = v[1];
                """,
            ),
        )

        graphing_points = []

        # Process each points data
        for i, (point_name, time_value_list) in enumerate(plot_data.items()):

            # Used to check if parameter lines need to be added to custom graph
            graphing_points.append(point_name) if plot_name == "Custom" else None

            # Filter data
            x_values, y_values = self._filter_valid_data(time_value_list)

            # Plot point
            plot_point = PlotPoint(
                point_name,
                plot,
                x_values,
                y_values,
                CHART_COLORS[i % len(CHART_COLORS)],
            )

            # Add to renderers
            renderers["line"][point_name] = plot_point.get_line()
            renderers["asterick"][point_name] = plot_point.get_asterick()

        # Add features
        self._add_parameter_lines(plot, plot_name, graphing_points)
        self._add_interactive_features(plot)
        self._add_toggles(renderers)
        self._apply_styling(plot)

        # Save and modify plot
        self._save_plot(plot, plot_name)
        self._modify_html(plot_name)
        self._open_plot(plot_name)

    def _add_parameter_lines(self, plot: figure, plot_name: str, point_names: List):
        """Generate a horizontal line on the graph for a parameter."""

        # Parameter plots
        parameter_plots = ["Haulage Amps", "Cutter Amps"]
        jna_points = [
        "LTramPhaseA",
        "LTramPhaseB",
        "LTramPhaseC",
        "RTramPhaseA",
        "RTramPhaseB",
        "RTramPhaseC"
        ]
        cutter_points = [
        "LCutterPhaseA",
        "LCutterPhaseB",
        "LCutterPhaseC",
        "RCutterPhaseA",
        "RCutterPhaseB",
        "RCutterPhaseC"
        ]

        if plot_name in parameter_plots:

            if self.jna_limit is not None and plot_name == "Haulage Amps":
                self._add_horizontal_line(plot, self.jna_limit, "JNA Current Limit")

            if self.cutter_limit is not None and plot_name == "Cutter Amps":
                self._add_horizontal_line(plot, self.cutter_limit, "Cutter Amp Limit")

        else:
            for point in point_names:

                if point in jna_points and self.jna_limit is not None:
                    self._add_horizontal_line(plot, self.jna_limit, "JNA Current Limit")

                if point in cutter_points and self.cutter_limit is not None:
                    self._add_horizontal_line(plot, self.cutter_limit, "Cutter Amp Limit")

    def _add_horizontal_line(self, plot: figure, value: int, label: str):
        """Add a horizontal line to the plot."""
        line = Span(
            location=value,
            dimension="width",
            line_color="white",
            line_width=2,
            line_dash="dashed",
            line_alpha=0.8,
        )
        plot.add_layout(line)

        label_annotation = Label(
            x=50,
            y=value + (value * 0.02),  # Slightly above the line
            x_units="screen",
            text=f"{label}: {value}A",
            text_color="white",
            text_font_size="10pt",
        )
        plot.add_layout(label_annotation)

    def _filter_valid_data(self, time_value_list: Dict):
        """Filter out Nan (empty) values in data."""

        # Convert data to numpy array for bokeh
        timestamps, values = zip(
            *[(entry["timestamp"], entry["value"]) for entry in time_value_list]
        )
        x_values = np.array(timestamps)
        y_values = np.array(values).astype(np.double)

        # Create mask for y-values
        mask = np.isfinite(y_values)

        # Get valid date values
        masked_timestamps = x_values[mask] // 10**9
        valid_dates = [datetime.datetime.fromtimestamp(ts) for ts in masked_timestamps]

        return valid_dates, y_values[mask]

    def _add_interactive_features(self, plot: figure):
        """Add interactive features to a plot."""
        hover = HoverTool(
            tooltips=[("Point", "$name"), ("Time", "@x{%F %T}"), ("Value", "@y")]
        )

        formatter_code = """
            function formatMilliseconds(ms) {
                const date = new Date(ms);
                const year = date.getUTCFullYear();
                const month = String(date.getUTCMonth() + 1).padStart(2, '0');
                const day = String(date.getUTCDate()).padStart(2, '0');
                const hours = String(date.getUTCHours()).padStart(2, '0');
                const minutes = String(date.getUTCMinutes()).padStart(2, '0');
                const seconds = String(date.getUTCSeconds()).padStart(2, '0');
                return `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`;
            }
            return formatMilliseconds(value);
        """
        custom_formatter = CustomJSHover(code=formatter_code)
        hover.formatters = {"@x": custom_formatter}
        plot.add_tools(hover)

    def _add_toggles(self, renderers: dict):
        """Add interactive toggle and checkbox buttons."""

        # Toggle symbols
        self.toggle_symbols_btn = Button(
            label="TOGGLE SYMBOLS",
            button_type="success",
            css_classes=["custom_button_bokeh"],
            height=50,
            width=50,
        )
        toggle_symbols = """
        for (var key in astericks){
            if (lines[key].visible) {
                astericks[key].visible = ! astericks[key].visible;
            }
        }
        """
        symbols_callback = CustomJS(
            args=dict(astericks=renderers["asterick"], lines=renderers["line"]),
            code=toggle_symbols,
        )
        self.toggle_symbols_btn.js_on_click(symbols_callback)

        # Checkboxes
        labels = list(renderers["line"].keys())
        self.checkboxes = CheckboxGroup(labels=labels)
        checkboxes_code = """
        const checked = new Set(this.active)
        for (let i = 0; i < labels.length; i++) {
            let point_name = labels[i]
            renderers["line"][point_name].visible = checked.has(i)
            if (renderers["asterick"][point_name].visible){
                renderers["asterick"][point_name].visible = ! renderers["asterick"][point_name].visible
            }
        }
        """
        checkboxes_callback = CustomJS(
            args={"renderers": renderers, "labels": labels}, code=checkboxes_code
        )
        self.checkboxes.js_on_change("active", checkboxes_callback)

    def _apply_styling(self, plot: figure):
        """Apply styling to plot."""

        # Axis formatter
        plot.xaxis.formatter = DatetimeTickFormatter(
            seconds="%H:%M:%S",
            minutes="%H:%M",
            hours="%H:%M",
            days="%m/%d",
            months="%m/%Y",
            years="%Y",
        )

        self.custom_css = """
        <style>
            body {
                background-color: #2e2e2e;
                color: white;
            }

            .custom_button_bokeh button.bk.bk-btn.bk-btn-success {
                background-color: lime;
                color: black;
                }
        </style>
        """
        self.custom_css_div = Div(text=self.custom_css)

    def _save_plot(self, plot: figure, name: str):
        """Save the plot to the output folder."""
        layout = column(
            self.custom_css_div, self.date_range_slider, plot, row(self.checkboxes, self.toggle_symbols_btn)
        )
        output_file(f"{DATA_FOLDER_PATH}/{name}.html")
        save(layout)

    def _modify_html(self, plot_name: str):
        """Post processing of HTML file with Beautiful Soup."""
        with open(
            DATA_FOLDER_PATH + "\\" + plot_name + ".html", "r", encoding="utf-8"
        ) as plot_file:
            soup = BeautifulSoup(plot_file, "html.parser")

            # <head> section of html
            head_tag = soup.head
            if head_tag:
                head_tag.append(BeautifulSoup(self.custom_css, "html.parser"))

            # <title> section of html
            title_tags = soup.find_all("title")
            for title in title_tags:
                title.string = plot_name

        with open(
            DATA_FOLDER_PATH + "\\" + plot_name + ".html", "w", encoding="utf-8"
        ) as plot_file:
            plot_file.write(str(soup))

    def _open_plot(self, plot_name):
        """Open plot in browser."""
        os.startfile(DATA_FOLDER_PATH + "\\" + plot_name + ".html")
