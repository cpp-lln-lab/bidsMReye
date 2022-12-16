from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

from bidsmreye.generalize import convert_confounds
from bidsmreye.generalize import perform_quality_control
from bidsmreye.utils import get_dataset_layout


def test_perform_quality_control():

    output_location = Path().resolve()
    output_location = output_location.joinpath("tests", "data", "bidsmreye")

    layout_out = get_dataset_layout(output_location)

    confounds_tsv = output_location.joinpath(
        "sub-01",
        "func",
        "sub-01_task-nback_space-MNI152NLin2009cAsym_desc-bidsmreye_confounds.tsv",
    )

    data = {"eye1_x_coordinate": [0, 1, 2], "eye1_y_coordinate": [0, 1, 2]}
    df = pd.DataFrame(data)
    df.to_csv(confounds_tsv, sep="\t", index=False)

    perform_quality_control(layout_out, confounds_tsv)


def test_convert_confounds():

    output_location = Path().resolve()
    output_location = output_location.joinpath("tests", "data", "bidsmreye")

    layout_out = get_dataset_layout(output_location)

    file = output_location.joinpath(
        "sub-01",
        "func",
        "sub-01_task-nback_space-MNI152NLin2009cAsym_desc-bidsmreye_confounds.npy",
    )
    shutil.copy(file, file.with_suffix(".bak"))

    confound_name = convert_confounds(layout_out, file)

    assert confound_name.is_file()

    confound_name.unlink()
    shutil.copy(file.with_suffix(".bak"), file)
    file.with_suffix(".bak").unlink()
