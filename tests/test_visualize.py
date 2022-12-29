from __future__ import annotations

from pathlib import Path

import pandas as pd

from .utils import create_confounds_tsv
from .utils import return_bidsmreye_eyetrack_tsv
from bidsmreye.visualize import group_report
from bidsmreye.visualize import visualize_eye_gaze_data


def test_visualize_eye_gaze_data():

    confounds_tsv = return_bidsmreye_eyetrack_tsv()

    create_confounds_tsv()

    eye_gaze_data = pd.read_csv(confounds_tsv, sep="\t")

    fig = visualize_eye_gaze_data(eye_gaze_data)

    fig.show()


def test_group_report():

    input_dir = Path().resolve().joinpath("tests", "data", "derivatives", "bidsmreye")

    group_report(input_dir)
