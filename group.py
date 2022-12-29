from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from bids import BIDSLayout
from plotly.subplots import make_subplots
from rich import print

# from bidsmreye._version import _version

# __version__ = _version.get_versions()["version"]
__version__ = "0.2.0"

FONT_SIZE = dict(size=14)
GRID_COLOR = "grey"
LINE_COLOR = "rgb(0, 150, 175)"
BG_COLOR = "rgb(255,255,255)"
COLOR_1 = "rgba(30, 120, 180, 0.6)"
COLOR_2 = "rgba(255, 130, 15, 0.6)"
COLOR_3 = "rgba(45, 160, 45, 0.6)"
X_POSITION_1 = 1
X_POSITION_2 = 1.5
X_POSITION_3 = 2

input_dir = "/home/remi/gin/Nilsonne/eyetrack_preproc/derivatives/bidsmreye"

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


print(qc_data)

nb_data_points = qc_data.shape[0]


fig = go.Figure()

fig = go.FigureWidget(
    make_subplots(
        rows=2,
        cols=3,
        horizontal_spacing=0.2,
        vertical_spacing=0.2,
        specs=[
            [{"rowspan": 1, "colspan": 3}, None, None],
            [{"rowspan": 1, "colspan": 2}, None, None],
        ],
    )
)

row = 1
col = 1

fig.add_trace(
    go.Box(
        x=np.ones(nb_data_points) * X_POSITION_1,
        y=qc_data["NbDisplacementOutliers"],
        marker=dict(color=COLOR_1),
        name="displacement",
    ),
    row=row,
    col=col,
)
fig.add_trace(
    go.Box(
        x=np.ones(nb_data_points) * X_POSITION_2,
        y=qc_data["NbXOutliers"],
        marker=dict(color=COLOR_2),
        name="x gaze<br>position",
    ),
    row=row,
    col=col,
)
fig.add_trace(
    go.Box(
        x=np.ones(nb_data_points) * X_POSITION_3,
        y=qc_data["NbYOutliers"],
        marker=dict(color=COLOR_3),
        name="Y gaze<br>position",
    ),
    row=row,
    col=col,
)

fig.update_xaxes(
    row=row,
    col=col,
    tickvals=[X_POSITION_1, X_POSITION_2, X_POSITION_3],
    ticktext=["Disp", "X", "Y"],
)

fig.update_yaxes(
    row=row,
    col=col,
    title=dict(text="number of outliers", font=FONT_SIZE),
)

row = 2
col = 1

fig.add_trace(
    go.Box(
        x=np.ones(nb_data_points) * X_POSITION_1,
        y=qc_data["eye1XVar"],
        marker=dict(color=COLOR_1),
        name="x gaze<br>position",
    ),
    row=row,
    col=col,
)
fig.add_trace(
    go.Box(
        x=np.ones(nb_data_points) * X_POSITION_2,
        y=qc_data["eye1YVar"],
        marker=dict(color=COLOR_2),
        name="Y gaze<br>position",
    ),
    row=row,
    col=col,
)

fig.update_xaxes(
    row=row,
    col=col,
    tickvals=[X_POSITION_1, X_POSITION_2],
    ticktext=["X", "Y"],
)

fig.update_yaxes(
    row=row,
    col=col,
    title=dict(text="variance (degrees<sup>2</sup>)", font=FONT_SIZE),
)

fig.update_yaxes(
    title=dict(standoff=0, font=FONT_SIZE),
    showline=True,
    linewidth=2,
    linecolor="black",
    zeroline=True,
    gridcolor=GRID_COLOR,
    griddash="dot",
    gridwidth=0.5,
    tickfont=dict(family="arial", color="black", size=FONT_SIZE["size"]),
)

fig.update_xaxes(
    tickangle=-45,
    ticks="outside",
    tickwidth=2,
    tickcolor="black",
    ticklen=5,
    zeroline=True,
    showline=True,
    linewidth=2,
    linecolor="black",
    tickfont=dict(family="arial", color="black", size=FONT_SIZE["size"]),
)

fig.update_traces(
    boxpoints="all",
    jitter=0.3,
    pointpos=2,
    boxmean=True,
    opacity=1,
    width=0.2,
    hovertext=qc_data["filename"],
    marker=dict(size=16, opacity=1),
    fillcolor="rgb(200, 200, 200)",
    line=dict(color="black"),
    unselected=dict(marker=dict(opacity=0.1)),
)

fig.update_layout(showlegend=False, plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR)

fig.update_layout(
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
    margin=dict(t=150, pad=0),
)

fig.show()
