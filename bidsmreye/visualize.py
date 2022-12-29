from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from . import _version
from bidsmreye.bids_utils import get_dataset_layout
from bidsmreye.bids_utils import list_subjects
from bidsmreye.configuration import Config
from bidsmreye.logging import bidsmreye_log
from bidsmreye.utils import check_if_file_found
from bidsmreye.utils import set_this_filter

__version__ = _version.get_versions()["version"]

LINE_WIDTH = 3
FONT_SIZE = dict(size=14)
GRID_COLOR = "grey"
LINE_COLOR = "rgb(0, 150, 175)"
BG_COLOR = "rgb(255,255,255)"
HEAT_MAP_COLOR = "gnbu"
MARKER_SIZE = 10

TICK_FONT = dict(family="arial", color="black", size=14)

X_POSITION_1 = 1
X_POSITION_2 = 1.5
X_POSITION_3 = 2
X_POSITION = [X_POSITION_1, X_POSITION_2, X_POSITION_3]

COLOR_1 = "rgba(30, 120, 180, 0.6)"
COLOR_2 = "rgba(255, 130, 15, 0.6)"
COLOR_3 = "rgba(45, 160, 45, 0.6)"
COLORS = [COLOR_1, COLOR_2, COLOR_3]

log = bidsmreye_log(name="bidsmreye")


def collect_group_qc_data(cfg: Config) -> pd.DataFrame:
    """Collect QC metrics data from all subjects json in a BIDS dataset.

    :param input_dir:
    :type input_dir: str | Path
    :return:
    :rtype: pd.DataFrame
    """
    layout = get_dataset_layout(cfg.output_dir, use_database=False)

    subjects = list_subjects(cfg, layout)

    this_filter = set_this_filter(cfg, subjects, "eyetrack_qc")

    bf = layout.get(
        return_type="filename",
        regex_search=True,
        **this_filter,
    )

    check_if_file_found(bf, this_filter, layout)

    qc_data = None
    for i, file in enumerate(bf):

        log.info(f"Processing file: {file}")

        entities = layout.parse_file_entities(file)

        with open(file) as f:
            data = json.loads(f.read())

        df = pd.json_normalize(data)
        df["filename"] = Path(file).name
        df["subject"] = entities["subject"]
        qc_data = df if i == 0 else pd.concat([qc_data, df], sort=False)

    cols = [
        "subject",
        "filename",
        "NbDisplacementOutliers",
        "NbXOutliers",
        "NbYOutliers",
        "eye1XVar",
        "eye1YVar",
    ]
    qc_data = qc_data[cols]  # type: ignore

    return qc_data


def plot_group_boxplot(
    fig: Any,
    qc_data: pd.DataFrame,
    row: int,
    col: int,
    column_names: list[str],
    trace_names: list[str],
    ticktext: list[str],
    yaxes_title: str,
) -> None:

    nb_data_points = qc_data.shape[0]

    for i, this_column in enumerate(column_names):
        fig.add_trace(
            go.Box(
                x=np.ones(nb_data_points) * X_POSITION[i],
                y=qc_data[this_column],
                marker=dict(size=MARKER_SIZE, color=COLORS[i]),
                name=trace_names[i],
            ),
            row=row,
            col=col,
        )
    fig.update_xaxes(
        row=row,
        col=col,
        tickvals=X_POSITION[: len(column_names)],
        ticktext=ticktext,
    )
    fig.update_yaxes(
        row=row,
        col=col,
        title=dict(text=yaxes_title, font=FONT_SIZE),
    )


def group_report(cfg: Config) -> None:
    """Create a group level report figure for eyetracking data.

    :return: Figure object
    :rtype: Any
    """
    qc_data = collect_group_qc_data(cfg)

    fig = go.FigureWidget(
        make_subplots(
            rows=2,
            cols=3,
            horizontal_spacing=0.2,
            vertical_spacing=0.1,
            specs=[
                [{"rowspan": 1, "colspan": 3}, None, None],
                [{"rowspan": 1, "colspan": 2}, None, None],
            ],
        )
    )

    row = 1
    col = 1

    plot_group_boxplot(
        fig,
        qc_data=qc_data,
        row=row,
        col=col,
        column_names=["NbDisplacementOutliers", "NbXOutliers", "NbYOutliers"],
        trace_names=["displacement", "x gaze<br>position", "Y gaze<br>position"],
        ticktext=["Disp", "X", "Y"],
        yaxes_title="number of outliers",
    )

    row = 2
    col = 1

    plot_group_boxplot(
        fig,
        qc_data=qc_data,
        row=row,
        col=col,
        column_names=["eye1XVar", "eye1YVar"],
        trace_names=["x gaze<br>position", "Y gaze<br>position"],
        ticktext=["X", "Y"],
        yaxes_title="variance (degrees<sup>2</sup>)",
    )

    fig.update_yaxes(
        title=dict(standoff=0, font=FONT_SIZE),
        showline=True,
        linewidth=LINE_WIDTH - 1,
        linecolor="black",
        gridcolor=GRID_COLOR,
        griddash="dot",
        gridwidth=0.5,
        tickfont=TICK_FONT,
    )

    fig.update_xaxes(
        showline=True,
        linewidth=LINE_WIDTH - 1,
        linecolor="black",
        ticks="outside",
        tickangle=-45,
        ticklen=5,
        tickwidth=2,
        tickcolor="black",
        tickfont=TICK_FONT,
    )

    fig.update_traces(
        boxpoints="all",
        jitter=0.3,
        pointpos=2,
        boxmean=True,
        width=0.2,
        hovertext=qc_data["filename"],
        marker=dict(size=MARKER_SIZE),
        fillcolor="rgb(200, 200, 200)",
        line=dict(color="black"),
    )

    fig.update_layout(
        showlegend=False,
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=BG_COLOR,
        height=800,
        width=800,
        title=dict(
            text=f"""<b>bidsmreye: group report</b><br>
    <b>Summary</b><br>
    - Date and time: {datetime.now():%Y-%m-%d, %H:%M}<br>
    - bidsmreye version: {__version__}<br>
            """,
            x=0.05,
            y=0.95,
            font=dict(size=19, color="black"),
        ),
        margin=dict(t=150, b=10, l=100, r=10, pad=0),
    )

    fig.show()
    group_report_file = Path(cfg.output_dir).joinpath("group_eyetrack.html")
    fig.write_html(group_report_file)

    qc_data_file = Path(cfg.output_dir).joinpath("group_eyetrack.tsv")
    qc_data.to_csv(qc_data_file, sep="\t", index=False)


def value_range(X: pd.Series) -> list[float]:
    return [-X.max() * 1.2, X.max() * 1.2]


def time_range(time_stamps: pd.Series) -> list[float]:
    return [time_stamps.min() - 3, time_stamps.max() + 3]


def visualize_eye_gaze_data(
    eye_gaze_data: pd.DataFrame,
) -> Any:

    fig = go.FigureWidget(
        make_subplots(
            rows=3,
            cols=4,
            shared_xaxes=True,
            horizontal_spacing=0.1,
            vertical_spacing=0.05,
            specs=[
                [{"colspan": 2}, None, {"rowspan": 2, "colspan": 2}, None],
                [{"colspan": 2}, None, None, None],
                [{"colspan": 2}, None, None, None],
            ],
        )
    )

    # Plot input signal together with split output signal (X & Y)
    plot_time_series(fig, eye_gaze_data, title_text="X", row=1, col=1)
    plot_time_series(fig, eye_gaze_data, title_text="Y", row=2, col=1)
    plot_time_series(
        fig,
        eye_gaze_data,
        title_text="displacement",
        row=3,
        col=1,
        plotting_range=[-0.1, eye_gaze_data["displacement"].max() * 1.1],
        line_color="grey",
    )
    fig.update_xaxes(
        row=3,
        col=1,
        title=dict(text="Time (s)", standoff=16, font=FONT_SIZE),
        tickfont=TICK_FONT,
    )

    plot_heat_map(fig, eye_gaze_data)

    return fig


def plot_time_series(
    fig: Any,
    eye_gaze_data: pd.DataFrame,
    title_text: str,
    row: int,
    col: int,
    plotting_range: list[float] | None = None,
    line_color: str = LINE_COLOR,
) -> None:

    outliers = None

    values_to_plot = eye_gaze_data["eye1_x_coordinate"]
    outliers = eye_gaze_data["eye1_x_outliers"]
    outlier_color = "orange"
    if title_text == "Y":
        values_to_plot = eye_gaze_data["eye1_y_coordinate"]
        outliers = eye_gaze_data["eye1_y_outliers"]
    elif title_text == "displacement":
        values_to_plot = eye_gaze_data["displacement"]
        outliers = eye_gaze_data["displacement_outliers"]
        outlier_color = "red"

    if plotting_range is None:
        plotting_range = value_range(values_to_plot)

    fig.add_trace(
        go.Scatter(
            x=time_range(eye_gaze_data["eye_timestamp"]),
            y=[0, 0],
            mode="lines",
            line_color="black",
            line_width=LINE_WIDTH - 1,
        ),
        row=row,
        col=col,
    )

    fig.add_trace(
        go.Scatter(
            x=eye_gaze_data["eye_timestamp"],
            y=values_to_plot,
            mode="lines",
            line_color=line_color,
            line_width=LINE_WIDTH,
        ),
        row=row,
        col=col,
    )

    if outliers is not None:
        fig.add_trace(
            go.Scatter(
                x=eye_gaze_data["eye_timestamp"][outliers == 1],
                y=values_to_plot[outliers == 1],
                mode="markers",
                marker_color=outlier_color,
                marker_size=MARKER_SIZE,
            ),
            row=row,
            col=col,
        )

    fig.update_xaxes(
        range=time_range(eye_gaze_data["eye_timestamp"]),
        row=row,
        col=col,
        gridcolor=GRID_COLOR,
        griddash="dot",
        gridwidth=0.5,
        tickfont=TICK_FONT,
    )
    fig.update_yaxes(
        range=plotting_range,
        row=row,
        col=col,
        gridcolor=GRID_COLOR,
        griddash="dot",
        gridwidth=0.5,
        ticksuffix="°",
        title=dict(text=title_text, standoff=0, font=FONT_SIZE),
        tickfont=FONT_SIZE,
    )

    fig.update_layout(
        showlegend=False,
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=BG_COLOR,
    )


def plot_heat_map(fig: Any, eye_gaze_data: pd.DataFrame) -> None:

    X = eye_gaze_data["eye1_x_coordinate"]
    Y = eye_gaze_data["eye1_y_coordinate"]

    x_range = value_range(X)
    y_range = value_range(Y)

    fig.add_trace(
        go.Histogram2dContour(x=X, y=Y, colorscale=HEAT_MAP_COLOR),
        row=1,
        col=3,
    )

    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=[0, 0],
            mode="lines",
            line_color="black",
            line_width=LINE_WIDTH - 2,
        ),
        row=1,
        col=3,
    )
    fig.add_trace(
        go.Scatter(
            x=[0, 0],
            y=y_range,
            mode="lines",
            line_color="black",
            line_width=LINE_WIDTH - 2,
        ),
        row=1,
        col=3,
    )

    fig.add_trace(
        go.Scatter(
            x=X,
            y=Y,
            opacity=0.4,
            line=dict(color="black", width=1, dash="dash"),
        ),
        row=1,
        col=3,
    )

    outliers = eye_gaze_data["eye1_x_outliers"]
    outlier_color = "orange"
    add_outliers_to_heatmap(fig, X, Y, outliers, outlier_color)
    outliers = eye_gaze_data["eye1_y_outliers"]
    add_outliers_to_heatmap(fig, X, Y, outliers, outlier_color)
    outliers = eye_gaze_data["displacement_outliers"]
    outlier_color = "red"
    add_outliers_to_heatmap(fig, X, Y, outliers, outlier_color)

    fig.update_xaxes(
        row=1,
        col=3,
        range=value_range(X),
        ticksuffix="°",
        title=dict(text="X", standoff=16, font=FONT_SIZE),
        tickfont=TICK_FONT,
    )
    fig.update_yaxes(
        row=1,
        col=3,
        range=value_range(Y),
        ticksuffix="°",
        title=dict(text="Y", standoff=16, font=FONT_SIZE),
        tickfont=TICK_FONT,
    )

    fig.update_layout(showlegend=False)


def add_outliers_to_heatmap(
    fig: Any, X: pd.Series, Y: pd.Series, outliers: pd.Series, outlier_color: str
) -> None:
    fig.add_trace(
        go.Scatter(
            x=X[outliers == 1],
            y=Y[outliers == 1],
            mode="markers",
            marker_color=outlier_color,
            marker_size=MARKER_SIZE / 2,
        ),
        row=1,
        col=3,
    )
