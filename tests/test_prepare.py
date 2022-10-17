from __future__ import annotations

from pathlib import Path

from bidsmreye.prepare_data import combine_data_with_empty_labels
from bidsmreye.utils import get_dataset_layout


def test_combine_data_with_empty_labels():

    output_location = Path().resolve()
    output_location = output_location.joinpath("tests", "data", "bidsmreye")

    layout_out = get_dataset_layout(output_location)

    file = output_location.joinpath(
        "sub-01",
        "func",
        "sub-01_task-nback_run-01_space-MNI152NLin2009cAsym_desc-eye_mask.p",
    )

    no_label_file = combine_data_with_empty_labels(layout_out, file)

    assert no_label_file.is_file()

    expected_file = output_location.joinpath(
        "sub-01",
        "func",
        "sub-01_task-nback_run-01_space-MNI152NLin2009cAsym_desc-nolabel_bidsmreye.npz",
    )

    assert no_label_file == expected_file

    no_label_file.unlink()
