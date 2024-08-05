from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from bidsmreye.bids_utils import create_bidsname, get_dataset_layout
from bidsmreye.configuration import Config
from bidsmreye.quality_control import (
    add_qc_to_sidecar,
    compute_displacement_and_outliers,
    compute_robust_outliers,
    get_sampling_frequency,
    perform_quality_control,
    quality_control_input,
    quality_control_output,
)

from .conftest import rm_dir


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


def test_get_sampling_frequency(output_dir):
    layout = get_dataset_layout(output_dir)

    file = layout.get(return_type="filename", suffix="eyetrack")[0]

    sampling_frequency = get_sampling_frequency(layout, file)

    assert sampling_frequency == 0.14285714285714285


@pytest.mark.xfail(reason="not implemented yet")
def test_get_sampling_frequency_in_root(data_dir):
    ds_location = data_dir / "ds000201-der"
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


def test_quality_control_output(
    create_basic_data, create_basic_json, bidsmreye_eyetrack_tsv, data_dir
):
    output_dir = data_dir

    df = pd.DataFrame(create_basic_data)
    df.to_csv(bidsmreye_eyetrack_tsv, sep="\t", index=False)

    cfg = Config(
        output_dir / "bidsmreye",
        output_dir,
    )

    quality_control_output(cfg)


def test_quality_control_input(tmp_path, data_dir):
    input_dir = data_dir / "ds000201-der"
    output_dir = tmp_path / "derivatives"

    cfg = Config(
        input_dir,
        output_dir,
    )

    quality_control_input(cfg)


def test_perform_quality_control(
    output_dir,
    pybids_test_dataset,
    create_basic_data,
    create_basic_json,
    bidsmreye_eyetrack_tsv,
):
    layout = get_dataset_layout(output_dir)

    df = pd.DataFrame(create_basic_data)
    df.to_csv(bidsmreye_eyetrack_tsv, sep="\t", index=False)

    cfg = Config(
        pybids_test_dataset,
        Path(__file__).parent / "data",
    )

    perform_quality_control(cfg, layout, bidsmreye_eyetrack_tsv)


def test_perform_quality_control_with_different_output(data_dir, pybids_test_dataset):
    input_dir = data_dir / "ds000201-der"
    layout_in = get_dataset_layout(input_dir)

    output_dir = input_dir / "derivatives" / "bidsmreye"
    layout_out = get_dataset_layout(output_dir)

    confounds_tsv = layout_in.get(
        return_type="filename", subject="9001", suffix="eyetrack", extension=".tsv"
    )[0]

    cfg = Config(
        pybids_test_dataset,
        Path(__file__).parent / "data",
    )

    perform_quality_control(
        cfg=cfg, layout_in=layout_in, confounds_tsv=confounds_tsv, layout_out=layout_out
    )

    rm_dir(output_dir)


def test_add_qc_to_sidecar(
    output_dir, create_confounds_tsv, create_basic_json, bidsmreye_eyetrack_tsv
):
    layout_out = get_dataset_layout(output_dir)

    confounds = pd.read_csv(bidsmreye_eyetrack_tsv, sep="\t")

    sidecar_name = create_bidsname(layout_out, bidsmreye_eyetrack_tsv, "confounds_json")

    add_qc_to_sidecar(confounds, sidecar_name)


def test_add_qc_to_sidecar_if_missing(data_dir):
    ds_location = data_dir / "ds000201-der"
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
