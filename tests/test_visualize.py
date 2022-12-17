from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from bidsmreye.quality_control import compute_displacement
from bidsmreye.quality_control import compute_robust_outliers
from bidsmreye.visualize import visualize_eye_gaze_data


def test_perform_quality_control():

    output_location = Path().resolve()
    output_location = output_location.joinpath("tests", "data", "bidsmreye")

    confounds_tsv = output_location.joinpath(
        "sub-01",
        "func",
        "sub-01_task-nback_space-MNI152NLin2009cAsym_desc-bidsmreye_eyetrack.tsv",
    )

    eye1_x_coordinate = np.random.randn(400)
    eye1_y_coordinate = np.random.randn(400)

    data = {
        "eye_timestamp": np.arange(400),
        "eye1_x_coordinate": eye1_x_coordinate,
        "eye1_y_coordinate": eye1_y_coordinate,
    }
    data["eye1_x_coordinate"][200] = (
        eye1_x_coordinate.mean() + eye1_x_coordinate.std() * 4
    )
    data["eye1_y_coordinate"][200] = (
        eye1_y_coordinate.mean() - eye1_y_coordinate.std() * 5
    )
    data["eye1_x_coordinate"][50] = eye1_x_coordinate.mean() - eye1_x_coordinate.std() * 5
    data["eye1_y_coordinate"][50] = eye1_y_coordinate.mean() + eye1_y_coordinate.std() * 4

    df = pd.DataFrame(data)
    df["displacement"] = compute_displacement(
        df["eye1_x_coordinate"], df["eye1_y_coordinate"]
    )
    df["outliers"] = compute_robust_outliers(df["displacement"])

    df.to_csv(confounds_tsv, sep="\t", index=False)

    eye_gaze_data = pd.read_csv(confounds_tsv, sep="\t")

    fig = visualize_eye_gaze_data(eye_gaze_data)

    fig.show()
