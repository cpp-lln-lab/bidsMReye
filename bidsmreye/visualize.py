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


def value_range(X: pd.Series) -> list[float]:
    return [-X.max() - 1, X.max() + 1]


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
        plotting_range=[-0.1, eye_gaze_data["displacement"].max() + 0.1],
        line_color="grey",
    )
    fig.update_xaxes(
        row=3,
        col=1,
        title=dict(text="Time (s)", standoff=16, font=FONT_SIZE),
        tickfont=FONT_SIZE,
    )

    plot_heat_map(
        fig, eye_gaze_data["eye1_x_coordinate"], eye_gaze_data["eye1_y_coordinate"]
    )

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
    if title_text == "Y":
        values_to_plot = eye_gaze_data["eye1_y_coordinate"]
    elif title_text == "displacement":
        values_to_plot = eye_gaze_data["displacement"]
        outliers = eye_gaze_data["outliers"]

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
                x=eye_gaze_data["eye_timestamp"],
                y=outliers,
                fillcolor="red",
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


def plot_heat_map(fig: Any, X: pd.Series, Y: pd.Series) -> None:

    x_range = value_range(X)
    y_range = value_range(Y)

    fig.add_trace(
        go.Histogram2dContour(x=X, y=Y, colorscale="Blues"),
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
            opacity=0.5,
            line=dict(color="black", width=1.5, dash="dash"),
        ),
        row=1,
        col=3,
    )

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
