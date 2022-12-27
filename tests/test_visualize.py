from __future__ import annotations

import pandas as pd

from .utils import bidsmreye_eyetrack
from .utils import create_confounds_tsv
from bidsmreye.visualize import visualize_eye_gaze_data


def test_visualize_eye_gaze_data():

    confounds_tsv = return_bidsmreye_eyetrack_tsv()

    create_confounds_tsv()

    eye_gaze_data = pd.read_csv(confounds_tsv, sep="\t")

    fig = visualize_eye_gaze_data(eye_gaze_data)

    fig.show()
