import os
from pathlib import Path

from bidsmreye.bidsutils import create_bidsname
from bidsmreye.bidsutils import get_dataset_layout
from bidsmreye.bidsutils import init_derivatives_layout
from bidsmreye.utils import return_path_rel_dataset


def test_write_dataset_description():

    output_location = Path().resolve()
    output_location = Path.joinpath(output_location, "derivatives")

    init_derivatives_layout(output_location)


def test_create_bidsname():

    output_location = Path().resolve()
    output_location = Path.joinpath(output_location, "derivatives")

    layout = get_dataset_layout(output_location)
    filename = (
        "inputs/raw/sub-pilot001/ses-001/anat/sub-pilot001_ses-001_acq-hires_UNIT1.nii"
    )

    output_file = create_bidsname(layout, filename=filename, filetype="mask")

    rel_path = return_path_rel_dataset(file_path=output_file, dataset_path=layout.root)
    assert (
        rel_path
        == "sub-pilot001/ses-001/anat/sub-pilot001_ses-001_acq-hires_desc-brain_mask.nii"
    )
