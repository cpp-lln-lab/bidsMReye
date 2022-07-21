import shutil
from pathlib import Path

import pytest

from bidsmreye.bidsutils import create_bidsname
from bidsmreye.bidsutils import get_bidsname_config
from bidsmreye.bidsutils import get_config
from bidsmreye.bidsutils import get_dataset_layout
from bidsmreye.bidsutils import get_pybids_config
from bidsmreye.bidsutils import init_derivatives_layout
from bidsmreye.utils import return_path_rel_dataset


def test_get_config_error():
    with pytest.raises(FileNotFoundError):
        get_config("", "foo.json")


def test_get_bidsname_config_smoke():
    get_bidsname_config()


def test_get_pybids_config_smoke():
    get_pybids_config()


def test_write_dataset_description():

    output_location = Path().resolve()
    output_location = Path.joinpath(output_location, "derivatives")

    init_derivatives_layout(output_location)

    shutil.rmtree(output_location)


def test_create_bidsname():

    output_location = Path().resolve()
    output_location = Path.joinpath(output_location, "derivatives")

    layout = get_dataset_layout(output_location)
    filename = "inputs/raw/sub-01/ses-01/func/sub-01_ses-01_task-motion_run-1_bold.nii"

    output_file = create_bidsname(layout, filename=filename, filetype="mask")

    rel_path = return_path_rel_dataset(file_path=output_file, dataset_path=layout.root)
    assert (
        rel_path == "sub-01/ses-01/func/sub-01_ses-01_task-motion_run-1_desc-eye_mask.p"
    )

    shutil.rmtree(output_location)
