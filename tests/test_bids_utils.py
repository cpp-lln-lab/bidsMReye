from __future__ import annotations

import json
import shutil
from pathlib import Path

from .utils import pybids_test_dataset
from bidsmreye.bids_utils import check_layout
from bidsmreye.bids_utils import create_bidsname
from bidsmreye.bids_utils import get_dataset_layout
from bidsmreye.bids_utils import init_dataset
from bidsmreye.bids_utils import list_subjects
from bidsmreye.configuration import Config
from bidsmreye.prepare_data import save_sampling_frequency_to_json
from bidsmreye.utils import set_this_filter


def test_create_bidsname():

    output_dir = Path().resolve()
    output_dir = Path.joinpath(output_dir, "derivatives")

    layout = get_dataset_layout(output_dir)
    filename = Path("inputs").joinpath(
        "raw",
        "sub-01",
        "ses-01",
        "func",
        "sub-01_ses-01_task-motion_run-1_bold.nii",
    )

    output_file = create_bidsname(layout, filename=filename, filetype="mask")

    rel_path = output_file.relative_to(layout.root)

    assert rel_path == Path("sub-01").joinpath(
        "ses-01", "func", "sub-01_ses-01_task-motion_run-1_desc-eye_mask.p"
    )

    shutil.rmtree(output_dir)


def test_get_dataset_layout_smoke_test():
    get_dataset_layout(Path("data"))
    shutil.rmtree("data")


def test_init_dataset():

    output_dir = Path().resolve()
    output_dir = Path.joinpath(output_dir, "derivatives")

    cfg = Config(
        pybids_test_dataset(),
        output_dir,
    )

    init_dataset(cfg)

    shutil.rmtree(output_dir)


def test_list_subjects():

    cfg = Config(
        pybids_test_dataset(),
        Path(__file__).parent.joinpath("data"),
    )

    layout = get_dataset_layout(pybids_test_dataset())

    subjects = list_subjects(cfg, layout)
    assert len(subjects) == 5


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
    source = "foo"
    save_sampling_frequency_to_json(layout_in, bf[0], source)
    sidecar_name = create_bidsname(layout_in, bf[0], "confounds_json")
    with open(sidecar_name) as f:
        content = json.load(f)
    assert content["Sources"][0] == "foo"


def test_check_layout_prepare_data():

    cfg = Config(
        pybids_test_dataset(),
        Path(__file__).parent.joinpath("data"),
    )

    layout_in = get_dataset_layout(
        cfg.input_dir,
        use_database=True,
        config=["bids", "derivatives"],
        reset_database=True,
    )
    check_layout(cfg, layout_in)
