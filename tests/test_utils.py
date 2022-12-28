from __future__ import annotations

import shutil
from pathlib import Path

from .utils import pybids_test_dataset
from bidsmreye.bids_utils import get_dataset_layout
from bidsmreye.utils import copy_license
from bidsmreye.utils import get_deepmreye_filename
from bidsmreye.utils import return_deepmreye_output_filename
from bidsmreye.utils import return_regex


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
