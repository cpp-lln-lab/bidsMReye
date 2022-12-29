from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from .utils import create_basic_data
from .utils import create_basic_json
from .utils import create_confounds_tsv
from .utils import return_bidsmreye_eyetrack_tsv
from .utils import rm_dir
from bidsmreye.bids_utils import create_bidsname
from bidsmreye.bids_utils import get_dataset_layout
from bidsmreye.configuration import Config
from bidsmreye.quality_control import add_qc_to_sidecar
from bidsmreye.quality_control import compute_displacement_and_outliers
from bidsmreye.quality_control import compute_robust_outliers
from bidsmreye.quality_control import get_sampling_frequency
from bidsmreye.quality_control import perform_quality_control
from bidsmreye.quality_control import quality_control_input
from bidsmreye.quality_control import quality_control_output


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


def test_get_sampling_frequency():

    ds_location = Path().resolve().joinpath("tests", "data", "bidsmreye")
    layout = get_dataset_layout(ds_location)

    file = layout.get(return_type="filename", suffix="eyetrack")[0]

    sampling_frequency = get_sampling_frequency(layout, file)

    assert sampling_frequency == 0.14285714285714285


@pytest.mark.xfail(reason="not implemented yet")
def test_get_sampling_frequency_in_root():

    ds_location = Path().resolve().joinpath("tests", "data", "ds000201-der")
    layout = get_dataset_layout(ds_location)

    file = layout.get(return_type="filename", subject="9001", suffix="eyetrack")[0]

    sampling_frequency = get_sampling_frequency(layout, file)

    assert sampling_frequency == 0.14285714285714285


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


def test_quality_control_output():

    create_basic_json()

    output_dir = Path().resolve()
    output_dir = output_dir.joinpath("tests", "data")

    confounds_tsv = return_bidsmreye_eyetrack_tsv()

    df = pd.DataFrame(create_basic_data())
    df.to_csv(confounds_tsv, sep="\t", index=False)

    cfg = Config(
        output_dir.joinpath("bidsmreye"),
        output_dir,
    )

    quality_control_output(cfg)


def test_quality_control_input():

    input_dir = Path().resolve().joinpath("tests", "data", "ds000201-der")
    output_dir = input_dir.joinpath("derivatives")

    rm_dir(output_dir)

    cfg = Config(
        input_dir,
        output_dir,
    )

    quality_control_input(cfg)

    rm_dir(output_dir)


def test_perform_quality_control():

    create_basic_json()

    output_dir = Path().resolve()
    output_dir = output_dir.joinpath("tests", "data", "bidsmreye")
    layout = get_dataset_layout(output_dir)
    confounds_tsv = return_bidsmreye_eyetrack_tsv()

    df = pd.DataFrame(create_basic_data())
    df.to_csv(confounds_tsv, sep="\t", index=False)

    perform_quality_control(layout, confounds_tsv)


def test_perform_quality_control_with_different_output():

    input_dir = Path().resolve().joinpath("tests", "data", "ds000201-der")
    layout_in = get_dataset_layout(input_dir)

    output_dir = input_dir.joinpath("derivatives", "bidsmreye")
    layout_out = get_dataset_layout(output_dir)

    confounds_tsv = layout_in.get(
        return_type="filename", subject="9001", suffix="eyetrack", extension=".tsv"
    )[0]

    perform_quality_control(
        layout_in=layout_in, confounds_tsv=confounds_tsv, layout_out=layout_out
    )

    rm_dir(output_dir)


def test_add_qc_to_sidecar():

    create_basic_json()

    create_confounds_tsv()

    output_dir = Path().resolve()
    output_dir = output_dir.joinpath("tests", "data", "bidsmreye")
    layout_out = get_dataset_layout(output_dir)

    confounds_tsv = return_bidsmreye_eyetrack_tsv()
    confounds = pd.read_csv(confounds_tsv, sep="\t")

    sidecar_name = create_bidsname(layout_out, confounds_tsv, "confounds_json")

    add_qc_to_sidecar(confounds, sidecar_name)


def test_add_qc_to_sidecar_if_missing():

    ds_location = Path().resolve().joinpath("tests", "data", "ds000201-der")
    layout = get_dataset_layout(ds_location)

    file = layout.get(
        return_type="filename", subject="9001", suffix="eyetrack", extension=".tsv"
    )[0]

    confounds = pd.read_csv(file, sep="\t")

    compute_displacement_and_outliers(confounds)

    sidecar_name = create_bidsname(layout, file, "confounds_json")

    add_qc_to_sidecar(confounds, sidecar_name)

    assert sidecar_name.exists()

    sidecar_name.unlink()
