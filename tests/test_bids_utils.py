from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from bidsmreye.bids_utils import (
    check_layout,
    create_bidsname,
    get_dataset_layout,
    init_dataset,
    list_subjects,
)
from bidsmreye.configuration import Config
from bidsmreye.prepare_data import save_sampling_frequency_to_json
from bidsmreye.utils import set_this_filter

from .utils import pybids_test_dataset


def test_create_bidsname(tmp_path):
    output_dir = tmp_path / "derivatives"

    layout = get_dataset_layout(output_dir)
    filename = Path("inputs").joinpath(
        "raw",
        "sub-01",
        "ses-01",
        "func",
        "sub-01_ses-01_task-motion_run-01_bold.nii",
    )

    output_file = create_bidsname(layout, filename=filename, filetype="mask")

    rel_path = output_file.relative_to(layout.root)

    assert rel_path == Path("sub-01").joinpath(
        "ses-01", "func", "sub-01_ses-01_task-motion_run-01_desc-eye_mask.p"
    )


def test_get_dataset_layout_smoke_test(tmp_path):
    get_dataset_layout(tmp_path / "data")


def test_init_dataset(tmp_path):
    output_dir = tmp_path / "derivatives"

    cfg = Config(
        pybids_test_dataset(),
        output_dir,
    )

    init_dataset(cfg)


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


def test_check_layout_error_no_space_entity(tmp_path):
    shutil.copytree(pybids_test_dataset(), tmp_path, dirs_exist_ok=True)
    for file in tmp_path.rglob("*_space-*"):
        file.unlink()

    cfg = Config(
        tmp_path,
        tmp_path / "foo",
    )

    print(cfg.input_dir)

    layout_in = get_dataset_layout(
        cfg.input_dir,
        use_database=False,
        config=["bids", "derivatives"],
        reset_database=True,
    )

    with pytest.raises(
        RuntimeError, match="does not have any data to process for filter"
    ):
        check_layout(cfg, layout_in)
