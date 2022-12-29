from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from bids import BIDSLayout
from plotly.subplots import make_subplots


# from bidsmreye._version import _version

# __version__ = _version.get_versions()["version"]
__version__ = "0.2.0"

input_dir = "/home/remi/gin/Nilsonne/eyetrack_preproc/derivatives/bidsmreye"


FONT_SIZE = dict(size=14)
GRID_COLOR = "grey"
LINE_COLOR = "rgb(0, 150, 175)"
BG_COLOR = "rgb(255,255,255)"
COLOR_1 = "rgba(30, 120, 180, 0.6)"
COLOR_2 = "rgba(255, 130, 15, 0.6)"
COLOR_3 = "rgba(45, 160, 45, 0.6)"
COLORS = [COLOR_1, COLOR_2, COLOR_3]
X_POSITION_1 = 1
X_POSITION_2 = 1.5
X_POSITION_3 = 2
X_POSITION = [X_POSITION_1, X_POSITION_2, X_POSITION_3]


def collect_group_data(input_dir: str | Path) -> pd.DataFrame:

    layout = BIDSLayout(input_dir)

    bf = layout.get(
        return_type="filename",
        desc="bidsmreye",
        suffix="eyetrack",
        extension="json",
    )

    qc_data = None
    for i, file in enumerate(bf):

        entities = layout.parse_file_entities(file)

        with open(file) as f:
            data = json.loads(f.read())

        df = pd.json_normalize(data)
        df["filename"] = Path(file).name
        df["Subject"] = entities["subject"]
        qc_data = df if i == 0 else pd.concat([qc_data, df], sort=False)

    return qc_data


def plot_group_boxplot(
    fig,
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
                marker=dict(color=COLORS[i]),
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


def main():

    qc_data = collect_group_data(input_dir)

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
        linewidth=2,
        linecolor="black",
        gridcolor=GRID_COLOR,
        griddash="dot",
        gridwidth=0.5,
        tickfont=dict(family="arial", color="black", size=FONT_SIZE["size"]),
    )

    fig.update_xaxes(
        showline=True,
        linewidth=2,
        linecolor="black",
        ticks="outside",
        tickangle=-45,
        ticklen=5,
        tickwidth=2,
        tickcolor="black",
        tickfont=dict(family="arial", color="black", size=FONT_SIZE["size"]),
    )

    fig.update_traces(
        boxpoints="all",
        jitter=0.3,
        pointpos=2,
        boxmean=True,
        width=0.2,
        hovertext=qc_data["filename"],
        marker=dict(size=16),
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


if __name__ == "__main__":
    main()
