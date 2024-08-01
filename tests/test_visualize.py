from __future__ import annotations

from pathlib import Path

import pandas as pd

from bidsmreye.bidsmreye import bidsmreye
from bidsmreye.configuration import Config
from bidsmreye.visualize import group_report, visualize_eye_gaze_data

from .utils import create_confounds_tsv, return_bidsmreye_eyetrack_tsv


def test_visualize_eye_gaze_data():
    confounds_tsv = return_bidsmreye_eyetrack_tsv()

    create_confounds_tsv()

    eye_gaze_data = pd.read_csv(confounds_tsv, sep="\t")

    fig = visualize_eye_gaze_data(eye_gaze_data)

    fig.show()


def test_group_report():
    input_dir = Path().resolve().joinpath("tests", "data", "derivatives", "bidsmreye")

    cfg = Config(
        input_dir=input_dir,
        output_dir=input_dir.parent,
    )

    group_report(cfg)


def test_group_report_cli():
    bids_dir = Path().resolve().joinpath("tests", "data", "derivatives", "bidsmreye")

    bidsmreye(
        bids_dir=bids_dir,
        output_dir=bids_dir.parent,
        analysis_level="group",
        action="qc",
        participant_label=["9001", "9008"],
    )
