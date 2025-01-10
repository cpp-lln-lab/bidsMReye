from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from bidsmreye.quality_control import compute_displacement, compute_robust_outliers


@pytest.fixture
def pybids_test_dataset(data_dir) -> Path:
    return data_dir / "synthetic" / "derivatives" / "fmriprep"


@pytest.fixture
def data_dir():
    return Path(__file__).parent / "data"


@pytest.fixture
def output_dir(tmp_path, data_dir) -> Path:
    src_dir = data_dir / "bidsmreye"
    target_dir = tmp_path / "bidsmreye"
    target_dir.mkdir()
    shutil.copytree(src_dir, target_dir, dirs_exist_ok=True)
    return target_dir


@pytest.fixture
def bidsmreye_eyetrack_tsv(output_dir):
    return (
        output_dir
        / "sub-01"
        / "func"
        / "sub-01_task-nback_space-MNI152NLin2009cAsym_desc-bidsmreye_eyetrack.tsv"
    )


@pytest.fixture
def create_basic_data():
    return {
        "x_coordinate": np.random.randn(400),
        "y_coordinate": np.random.randn(400),
    }


@pytest.fixture
def create_basic_json(output_dir):
    sidecar_name = (
        output_dir
        / "sub-01"
        / "func"
        / "sub-01_task-nback_space-MNI152NLin2009cAsym_desc-bidsmreye_eyetrack.json"
    )

    content = {"SamplingFrequency": 0.14285714285714285}

    json.dump(content, open(sidecar_name, "w"), indent=4)


@pytest.fixture
def create_confounds_tsv(bidsmreye_eyetrack_tsv, generate_confounds_tsv):
    generate_confounds_tsv(bidsmreye_eyetrack_tsv)


@pytest.fixture
def generate_confounds_tsv(create_data_with_outliers):

    def _generate_confounds_tsv(filename):
        df = pd.DataFrame(create_data_with_outliers)

        df["displacement"] = compute_displacement(
            df["x_coordinate"],
            df["y_coordinate"],
        )
        df["x_outliers"] = compute_robust_outliers(
            df["x_coordinate"], outlier_type="Carling"
        )
        df["y_outliers"] = compute_robust_outliers(
            df["y_coordinate"], outlier_type="Carling"
        )
        df["displacement_outliers"] = compute_robust_outliers(
            df["displacement"], outlier_type="Carling"
        )

        cols = df.columns.tolist()
        cols.insert(0, cols.pop(cols.index("timestamp")))
        df = df[cols]

        df.to_csv(filename, sep="\t", index=False)

    return _generate_confounds_tsv


@pytest.fixture
def create_data_with_outliers(create_basic_data):
    data = create_basic_data

    data["timestamp"] = np.arange(400)

    x_coordinate = data["x_coordinate"]
    y_coordinate = data["y_coordinate"]

    data["x_coordinate"][200] = x_coordinate.mean() + x_coordinate.std() * 4
    data["y_coordinate"][200] = y_coordinate.mean() - y_coordinate.std() * 5
    data["x_coordinate"][50] = x_coordinate.mean() - x_coordinate.std() * 5
    data["y_coordinate"][50] = y_coordinate.mean() + y_coordinate.std() * 4

    return data


def rm_dir(some_dir):
    if Path(some_dir).is_dir():
        shutil.rmtree(some_dir, ignore_errors=False)
