from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .utils import bidsmreye_eyetrack
from .utils import create_basic_data
from .utils import create_basic_json
from .utils import create_confounds_tsv
from bidsmreye.quality_control import add_qc_to_sidecar
from bidsmreye.quality_control import compute_robust_outliers
from bidsmreye.quality_control import perform_quality_control
from bidsmreye.quality_control import quality_control
from bidsmreye.utils import Config
from bidsmreye.utils import get_dataset_layout


def time_series():

    return [
        0.6876,
        0.9751,
        0.1322,
        0.2420,
        1.4233,
        1.2617,
        -0.8619,
        -0.9471,
        2.6217,
        -0.6192,
        -1.0646,
        -0.4872,
        -0.1146,
        0.3007,
        -0.4089,
        0.1137,
        -0.0946,
        0.7829,
        1.8999,
        -1.0088,
    ]


def test_compute_robust_outliers():

    outliers = compute_robust_outliers(pd.Series(time_series()))

    expected_outliers = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    assert outliers == expected_outliers


def test_compute_robust_outliers_carling():

    series = time_series()
    series[8] = 10
    outliers = compute_robust_outliers(pd.Series(series), outlier_type="Carling")

    expected_outliers = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    assert outliers == expected_outliers


def test_compute_robust_outliers_carling_with_nan():

    series = time_series()
    series[1] = np.nan
    series[8] = 10
    outliers = compute_robust_outliers(pd.Series(series), outlier_type="Carling")

    expected_outliers = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    assert outliers == expected_outliers


def test_compute_robust_with_nan():

    series = time_series()
    series[1] = np.nan
    series[8] = 10

    outliers = compute_robust_outliers(pd.Series(series))

    expected_outliers = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    assert outliers == expected_outliers


def test_quality_control():

    create_basic_json()

    output_location = Path().resolve()
    output_location = output_location.joinpath("tests", "data")

    confounds_tsv = bidsmreye_eyetrack()

    df = pd.DataFrame(create_basic_data())
    df.to_csv(confounds_tsv, sep="\t", index=False)

    cfg = Config(
        output_location,
        output_location,
    )

    quality_control(cfg)


def test_perform_quality_control():

    create_basic_json()

    output_location = Path().resolve()
    output_location = output_location.joinpath("tests", "data", "bidsmreye")
    layout_out = get_dataset_layout(output_location)
    confounds_tsv = bidsmreye_eyetrack()

    df = pd.DataFrame(create_basic_data())
    df.to_csv(confounds_tsv, sep="\t", index=False)

    perform_quality_control(layout_out, confounds_tsv)


def test_add_qc_to_sidecar():

    create_basic_json()

    create_confounds_tsv()

    output_location = Path().resolve()
    output_location = output_location.joinpath("tests", "data", "bidsmreye")
    layout_out = get_dataset_layout(output_location)
    confounds_tsv = bidsmreye_eyetrack()

    add_qc_to_sidecar(layout_out, confounds_tsv)
