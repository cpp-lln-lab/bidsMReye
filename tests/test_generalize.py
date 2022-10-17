from __future__ import annotations

from pathlib import Path

from bids.tests import get_test_data_path

from bidsmreye.generalize import convert_confounds
from bidsmreye.utils import get_dataset_layout


def test_convert_confounds():

    output_location = Path().resolve()
    output_location = output_location.joinpath("tests", "data", "bidsmreye")

    layout_out = get_dataset_layout(output_location)

    file = output_location.joinpath(
        "sub-01",
        "func",
        "sub-01_task-nback_space-MNI152NLin2009cAsym_desc-bidsmreye_confounds.npy",
    )

    confound_name = convert_confounds(layout_out, file)

    assert confound_name.is_file()

    confound_name.unlink()
