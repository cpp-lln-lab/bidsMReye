from __future__ import annotations

from pathlib import Path

from bidsmreye.bids_utils import get_dataset_layout
from bidsmreye.prepare_data import combine_data_with_empty_labels


def test_combine_data_with_empty_labels():

    output_dir = Path().resolve()
    output_dir = output_dir.joinpath("tests", "data", "bidsmreye")

    layout_out = get_dataset_layout(output_dir)

    file = output_dir.joinpath(
        "sub-01",
        "func",
        "sub-01_task-nback_run-01_space-MNI152NLin2009cAsym_desc-eye_mask.p",
    )

    no_label_file = combine_data_with_empty_labels(layout_out, file)

    assert no_label_file.is_file()

    expected_file = output_dir.joinpath(
        "sub-01",
        "func",
        "sub-01_task-nback_run-01_space-MNI152NLin2009cAsym_desc-nolabel_bidsmreye.npz",
    )

    assert no_label_file == expected_file

    no_label_file.unlink()
