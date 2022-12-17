from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

OPACITY = 1
LINE_WIDTH = 3
FONT_SIZE = dict(size=14)
GRID_COLOR = "grey"
LINE_COLOR = "rgb(0, 150, 175)"
BG_COLOR = "rgb(255,255,255)"
HEAT_MAP_COLOR = "gnbu"


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
            horizontal_spacing=0.05,
            vertical_spacing=0.1,
            shared_xaxes="columns",
            specs=[
                [{"colspan": 2}, None, {"rowspan": 2, "colspan": 2}, None],
                [{"colspan": 2}, None, None, None],
                [{"colspan": 2}, None, {"colspan": 2}, None],
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
        tickfont=FONT_SIZE,
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
            opacity=OPACITY,
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
            opacity=OPACITY,
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
                marker_size=10,
                opacity=OPACITY,
            ),
            row=row,
            col=col,
        )

    fig.update_xaxes(
        range=time_range(eye_gaze_data["eye_timestamp"]),
        row=row,
        col=col,
        gridcolor=GRID_COLOR,
        tickfont=FONT_SIZE,
    )
    fig.update_yaxes(
        range=plotting_range,
        row=row,
        col=col,
        gridcolor=GRID_COLOR,
        ticksuffix="°",
        title=dict(text=title_text, standoff=0, font=FONT_SIZE),
        tickfont=FONT_SIZE,
    )

    fig.update_layout(showlegend=False, plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR)


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
            opacity=OPACITY,
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
            opacity=OPACITY,
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
        tickfont=FONT_SIZE,
    )
    fig.update_yaxes(
        row=1,
        col=3,
        range=value_range(Y),
        ticksuffix="°",
        title=dict(text="Y", standoff=16, font=FONT_SIZE),
        tickfont=FONT_SIZE,
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
            marker_size=8,
            opacity=OPACITY,
        ),
        row=1,
        col=3,
    )
