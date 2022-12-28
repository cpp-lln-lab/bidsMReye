from __future__ import annotations

import shutil
from pathlib import Path

from .utils import pybids_test_dataset
from bidsmreye.bids_utils import create_bidsname
from bidsmreye.bids_utils import get_dataset_layout
from bidsmreye.bids_utils import init_dataset
from bidsmreye.bids_utils import list_subjects
from bidsmreye.configuration import Config


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
