from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

OPACITY = 1
LINE_WIDTH = 3
FONT_SIZE = dict(size=14)
GRID_COLOR = "white"
LINE_COLOR = "rgb(0, 150, 175)"


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

    time_stamps = eye_gaze_data["eye_timestamp"]
    X = eye_gaze_data["eye1_x_coordinate"]
    Y = eye_gaze_data["eye1_y_coordinate"]
    displacement = eye_gaze_data["displacement"]

    # Plot input signal together with split output signal (X & Y)
    plot_time_series(fig, X, time_stamps, title_text="X", row=1, col=1)
    plot_time_series(fig, Y, time_stamps, title_text="Y", row=2, col=1)
    plot_time_series(
        fig,
        displacement,
        time_stamps,
        title_text="displacement",
        row=3,
        col=1,
        plotting_range=[-0.1, displacement.max() + 0.1],
        line_color="grey",
    )
    fig.update_xaxes(
        row=3,
        col=1,
        title=dict(text="Time (s)", standoff=16, font=FONT_SIZE),
        tickfont=FONT_SIZE,
    )

    plot_heat_map(fig, X, Y)

    return fig


def plot_time_series(
    fig: Any,
    series: pd.Series,
    time_stamps: pd.Series,
    title_text: str,
    row: int,
    col: int,
    plotting_range: list[float] | None = None,
    line_color: str = LINE_COLOR,
) -> None:
    if plotting_range is None:
        plotting_range = value_range(series)
    fig.add_trace(
        go.Scatter(
            x=time_range(time_stamps),
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
            x=time_stamps,
            y=series,
            mode="lines",
            line_color=line_color,
            opacity=OPACITY,
            line_width=LINE_WIDTH,
        ),
        row=row,
        col=col,
    )
    fig.update_xaxes(range=time_range(time_stamps), row=row, col=col, tickfont=FONT_SIZE)
    fig.update_yaxes(
        range=plotting_range,
        row=row,
        col=col,
        gridcolor=GRID_COLOR,
        ticksuffix="°",
        title=dict(text=title_text, standoff=0, font=FONT_SIZE),
        tickfont=FONT_SIZE,
    )

    fig.update_layout(showlegend=False)


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
            line_width=1,
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
            line_width=1,
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
