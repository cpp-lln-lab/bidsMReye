from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from bidsmreye.quality_control import compute_displacement
from bidsmreye.quality_control import compute_robust_outliers


def create_basic_json():

    output_location = Path().resolve()
    output_location = output_location.joinpath("tests", "data", "bidsmreye")

    sidecar_name = output_location.joinpath(
        "sub-01",
        "func",
        "sub-01_task-nback_space-MNI152NLin2009cAsym_desc-bidsmreye_eyetrack.json",
    )

    content = {"SamplingFrequency": 0.14285714285714285}

    json.dump(content, open(sidecar_name, "w"), indent=4)


def return_bidsmreye_eyetrack_tsv():

    output_location = Path().resolve()
    output_location = output_location.joinpath("tests", "data", "bidsmreye")

    return output_location.joinpath(
        "sub-01",
        "func",
        "sub-01_task-nback_space-MNI152NLin2009cAsym_desc-bidsmreye_eyetrack.tsv",
    )


def create_basic_data():
    return {
        "eye1_x_coordinate": np.random.randn(400),
        "eye1_y_coordinate": np.random.randn(400),
    }


def create_data_with_outliers():

    data = create_basic_data()

    data["eye_timestamp"] = np.arange(400)

    eye1_x_coordinate = data["eye1_x_coordinate"]
    eye1_y_coordinate = data["eye1_y_coordinate"]

    data["eye1_x_coordinate"][200] = (
        eye1_x_coordinate.mean() + eye1_x_coordinate.std() * 4
    )
    data["eye1_y_coordinate"][200] = (
        eye1_y_coordinate.mean() - eye1_y_coordinate.std() * 5
    )
    data["eye1_x_coordinate"][50] = eye1_x_coordinate.mean() - eye1_x_coordinate.std() * 5
    data["eye1_y_coordinate"][50] = eye1_y_coordinate.mean() + eye1_y_coordinate.std() * 4

    return data


def create_confounds_tsv():

    confounds_tsv = return_bidsmreye_eyetrack_tsv()

    df = pd.DataFrame(create_data_with_outliers())

    df["displacement"] = compute_displacement(
        df["eye1_x_coordinate"],
        df["eye1_y_coordinate"],
    )
    df["eye1_x_outliers"] = compute_robust_outliers(
        df["eye1_x_coordinate"], outlier_type="Carling"
    )
    df["eye1_y_outliers"] = compute_robust_outliers(
        df["eye1_y_coordinate"], outlier_type="Carling"
    )
    df["displacement_outliers"] = compute_robust_outliers(
        df["displacement"], outlier_type="Carling"
    )

    cols = df.columns.tolist()
    cols.insert(0, cols.pop(cols.index("eye_timestamp")))
    df = df[cols]

    df.to_csv(confounds_tsv, sep="\t", index=False)
