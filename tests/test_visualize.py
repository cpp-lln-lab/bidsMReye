from __future__ import annotations

import shutil

import pandas as pd

from bidsmreye.bidsmreye import bidsmreye
from bidsmreye.configuration import Config
from bidsmreye.visualize import group_report, visualize_eye_gaze_data


def test_visualize_eye_gaze_data(create_confounds_tsv, bidsmreye_eyetrack_tsv):
    eye_gaze_data = pd.read_csv(bidsmreye_eyetrack_tsv, sep="\t")
    fig = visualize_eye_gaze_data(eye_gaze_data)
    fig.show()


def test_group_report(tmp_path, data_dir):
    src_dir = data_dir / "derivatives" / "bidsmreye"
    target_dir = tmp_path / "bidsmreye"
    target_dir.mkdir()
    shutil.copytree(src_dir, target_dir, dirs_exist_ok=True)

    cfg = Config(
        input_dir=target_dir,
        output_dir=target_dir.parent,
    )

    group_report(cfg)

    assert (target_dir / "group_eyetrack.html").exists()
    assert (target_dir / "group_eyetrack.tsv").exists()


def test_group_report_cli(tmp_path, data_dir):

    src_dir = data_dir / "derivatives" / "bidsmreye"
    target_dir = tmp_path / "bidsmreye"
    target_dir.mkdir()
    shutil.copytree(src_dir, target_dir, dirs_exist_ok=True)

    bidsmreye(
        bids_dir=target_dir,
        output_dir=target_dir.parent,
        analysis_level="group",
        action="qc",
        participant_label=["9001", "9008"],
    )

    assert (target_dir / "group_eyetrack.html").exists()
    assert (target_dir / "group_eyetrack.tsv").exists()
