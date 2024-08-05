from __future__ import annotations

from pathlib import Path

from bidsmreye.bids_utils import create_bidsname, get_dataset_layout
from bidsmreye.prepare_data import combine_data_with_empty_labels


def test_combine_data_with_empty_labels():
    output_dir = Path().absolute()
    output_dir = output_dir.joinpath("tests", "data", "bidsmreye")

    layout_out = get_dataset_layout(output_dir)

    file = output_dir.joinpath(
        "sub-01",
        "func",
        "sub-01_task-nback_run-01_space-MNI152NLin2009cAsym_desc-eye_mask.p",
    )

    no_label_file = combine_data_with_empty_labels(layout_out, file)

    assert no_label_file.exists()

    output_file = create_bidsname(layout_out, file, "no_label")
    file_to_move = Path(layout_out.root).joinpath("..", "bidsmreye", output_file.name)
    assert no_label_file == file_to_move

    no_label_file.unlink()
