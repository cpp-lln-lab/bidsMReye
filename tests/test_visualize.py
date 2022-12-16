from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from bidsmreye.visualize import visualize_eye_gaze_data


def test_perform_quality_control():

    output_location = Path().resolve()
    output_location = output_location.joinpath("tests", "data", "bidsmreye")

    confounds_tsv = output_location.joinpath(
        "sub-01",
        "func",
        "sub-01_task-nback_space-MNI152NLin2009cAsym_desc-bidsmreye_eyetrack.tsv",
    )

    data = {
        "eye_timestamp": np.arange(200),
        "eye1_x_coordinate": np.random.randn(200),
        "eye1_y_coordinate": np.random.randn(200),
    }
    df = pd.DataFrame(data)
    df.to_csv(confounds_tsv, sep="\t", index=False)

    eye_gaze_data = pd.read_csv(confounds_tsv, sep="\t")

    fig = visualize_eye_gaze_data(eye_gaze_data)

    fig.show()
