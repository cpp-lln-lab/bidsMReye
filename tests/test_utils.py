from __future__ import annotations

import shutil
from pathlib import Path

from .utils import pybids_test_dataset
from bidsmreye.bids_utils import get_dataset_layout
from bidsmreye.configuration import Config
from bidsmreye.utils import copy_license
from bidsmreye.utils import get_deepmreye_filename
from bidsmreye.utils import return_deepmreye_output_filename
from bidsmreye.utils import return_regex
from bidsmreye.utils import set_this_filter


def test_copy_license():

    output_dir = Path().resolve()
    output_dir = output_dir.joinpath("derivatives")

    shutil.rmtree(output_dir, ignore_errors=True)

    license_file = copy_license(output_dir)

    assert license_file.is_file()
    assert str(license_file) == str(output_dir.joinpath("LICENSE"))

    copy_license(output_dir)

    shutil.rmtree(output_dir)


def test_get_deepmreye_filename():

    layout = get_dataset_layout(pybids_test_dataset())

    output_file = Path(pybids_test_dataset()).joinpath(
        "sub-01",
        "ses-01",
        "func",
        "mask_sub-01_ses-01_task-nback_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.p",
    )

    img = layout.get(
        return_type="filename",
        subject="01",
        suffix="bold",
        task="nback",
        space="MNI152NLin2009cAsym",
        extension=".nii.gz",
    )
    deepmreye_mask_name = get_deepmreye_filename(layout, img, "mask")

    assert deepmreye_mask_name == output_file


def test_return_deepmreye_output_filename():

    input_file = "sub-01_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"
    output_filename = return_deepmreye_output_filename(input_file, "mask")
    expected_output_file = (
        "mask_sub-01_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.p"
    )
    assert output_filename == expected_output_file

    input_file = "sub-01_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii"
    output_filename = return_deepmreye_output_filename(input_file, "mask")
    assert output_filename == expected_output_file


def test_return_regex():
    assert return_regex("foo") == "^foo$"
    assert return_regex("^foo") == "^foo$"
    assert return_regex("foo$") == "^foo$"
    assert return_regex(["foo", "bar"]) == "^foo$|^bar$"


def test_set_this_filter_bold():

    output_dir = Path().resolve()
    output_dir = Path.joinpath(output_dir, "derivatives")

    cfg = Config(
        pybids_test_dataset(),
        output_dir,
    )

    this_filter = set_this_filter(cfg, subject_label="001", filter_type="bold")

    # remove keys that are not always sorted
    this_filter.pop("space")
    this_filter.pop("task")

    assert this_filter == {
        "datatype": "func",
        "extension": "nii.*",
        "run": "1|2",
        "subject": "001",
        "suffix": "^bold$",
    }


def test_set_this_filter_bidsmreye():

    output_dir = Path().resolve()
    output_dir = Path.joinpath(output_dir, "data", "bidsmreye")

    cfg = Config(pybids_test_dataset(), output_dir, run="1")

    this_filter = set_this_filter(cfg, subject_label="001", filter_type="eyetrack")

    # remove keys that are not always sorted
    this_filter.pop("task")

    assert this_filter == {
        "extension": "tsv",
        "run": "1",
        "subject": "001",
        "suffix": "^eyetrack$$",
    }


def test_set_this_filter_with_bids_filter_file():

    bids_filter = {
        "eyetrack": {"suffix": "^eyetrack$$", "extension": "tsv", "desc": "preproc"}
    }

    output_dir = Path().resolve()
    output_dir = Path.joinpath(output_dir, "data", "bidsmreye")

    cfg = Config(pybids_test_dataset(), output_dir, run="1", bids_filter=bids_filter)

    this_filter = set_this_filter(cfg, subject_label="001", filter_type="eyetrack")

    # remove keys that are not always sorted
    this_filter.pop("task")

    assert this_filter == {
        "extension": "tsv",
        "run": "1",
        "subject": "001",
        "suffix": "^eyetrack$$",
        "desc": "preproc",
    }
