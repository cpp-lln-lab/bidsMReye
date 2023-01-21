from __future__ import annotations

import json
from pathlib import Path

from .utils import pybids_test_dataset
from bidsmreye.bids_utils import create_bidsname
from bidsmreye.bids_utils import get_dataset_layout
from bidsmreye.configuration import Config
from bidsmreye.prepare_data import combine_data_with_empty_labels
from bidsmreye.prepare_data import save_sampling_frequency_to_json
from bidsmreye.utils import set_this_filter


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


def test_save_sampling_frequency_to_json():

    layout_in = get_dataset_layout(pybids_test_dataset())

    cfg = Config(
        pybids_test_dataset(),
        Path(__file__).parent.joinpath("data"),
    )

    this_filter = set_this_filter(cfg, "01", "bold")

    bf = layout_in.get(
        return_type="filename",
        regex_search=True,
        **this_filter,
    )
    save_sampling_frequency_to_json(layout_in, bf[0])
    sidecar_name = create_bidsname(layout_in, bf[0], "confounds_json")
    with open(sidecar_name) as f:
        content = json.load(f)
    assert (
        content["Sources"][0]
        == "sub-01"
        + "/ses-01"
        + "/func"
        + "/sub-01_ses-01_task-nback_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii"
    )
