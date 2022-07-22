import os
import shutil
from pathlib import Path
from pathlib import PurePath

from bids.tests import get_test_data_path

from bidsmreye.bidsutils import get_dataset_layout
from bidsmreye.utils import config
from bidsmreye.utils import get_deepmreye_filename
from bidsmreye.utils import list_subjects
from bidsmreye.utils import return_deepmreye_output_filename
from bidsmreye.utils import return_path_rel_dataset


def test_list_subjects():

    cfg = config()

    data_path = os.path.join(get_test_data_path(), "synthetic", "derivatives", "fmriprep")

    layout = get_dataset_layout(data_path)

    subjects = list_subjects(layout, cfg)
    assert len(subjects) == 5

    cfg["participant"] = ["02"]
    subjects = list_subjects(layout, cfg)
    assert subjects == ["02"]


def test_get_dataset_layout_smoke_test():
    get_dataset_layout("data")

    shutil.rmtree("data")


def test_return_path_rel_dataset():

    file_path = "/home/john/gin/datset/sub-03/func/sub-03_task-rest_space-T1w_desc-preproc_bold.nii.gz"
    dataset_path = "/home/john/gin/datset"
    rel_file_path = return_path_rel_dataset(file_path, dataset_path)

    assert (
        rel_file_path == "sub-03/func/sub-03_task-rest_space-T1w_desc-preproc_bold.nii.gz"
    )


def test_get_deepmreye_filename():

    data_path = os.path.join(get_test_data_path(), "synthetic", "derivatives", "fmriprep")

    layout = get_dataset_layout(data_path)

    output_file = PurePath(get_test_data_path()).joinpath(
        "synthetic",
        "derivatives",
        "fmriprep",
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

    assert deepmreye_mask_name == Path(output_file)


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
