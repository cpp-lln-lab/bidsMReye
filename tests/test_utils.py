import shutil
from pathlib import Path

import pytest
from bids.tests import get_test_data_path

from bidsmreye.bidsutils import get_dataset_layout
from bidsmreye.utils import Config
from bidsmreye.utils import config
from bidsmreye.utils import get_deepmreye_filename
from bidsmreye.utils import list_subjects
from bidsmreye.utils import return_deepmreye_output_filename


def pybids_test_dataset():
    return Path(get_test_data_path()).joinpath("synthetic", "derivatives", "fmriprep")


def test_Config():

    cfg = Config(
        pybids_test_dataset(),
        Path(__file__).parent.joinpath("data"),
    )
    assert not cfg.debug
    assert cfg.input_folder == pybids_test_dataset()
    assert cfg.output_folder == Path(__file__).parent.joinpath("data", "bidsmreye")
    assert sorted(cfg.participant) == ["01", "02", "03", "04", "05"]
    assert sorted(cfg.task) == ["nback", "rest"]
    assert sorted(cfg.space) == ["MNI152NLin2009cAsym", "T1w"]


def test_Config_task_omit_missing_values():
    cfg = Config(
        pybids_test_dataset(),
        Path(__file__).parent.joinpath("data"),
        task=["auditory", "rest"],
        participant=["01", "07"],
        space=["T1w", "T2w"],
    )
    assert cfg.participant == ["01"]
    assert cfg.task == ["rest"]
    assert cfg.space == ["T1w"]


def test_missing_subject():
    with pytest.warns(UserWarning):
        Config(
            pybids_test_dataset(),
            Path(__file__).parent.joinpath("data"),
            participant=["01", "07"],
        )


def test_no_subject():
    with pytest.raises(Exception) as e_info:
        Config(
            pybids_test_dataset(),
            Path(__file__).parent.joinpath("data"),
            participant=["99"],
        )
    assert e_info.type == RuntimeError


def test_missing_task():
    with pytest.warns(UserWarning):
        Config(
            pybids_test_dataset(),
            Path(__file__).parent.joinpath("data"),
            task=["auditory", "rest"],
        )


def test_no_task():
    with pytest.raises(Exception) as e_info:
        Config(
            pybids_test_dataset(),
            Path(__file__).parent.joinpath("data"),
            task=["foo"],
        )
    assert e_info.type == RuntimeError


def test_missing_space():
    with pytest.warns(UserWarning):
        Config(
            pybids_test_dataset(),
            Path(__file__).parent.joinpath("data"),
            space=["T1w", "T2w"],
        )


def test_no_subject():
    with pytest.raises(Exception) as e_info:
        Config(
            pybids_test_dataset(),
            Path(__file__).parent.joinpath("data"),
            space=["T2w"],
        )
    assert e_info.type == RuntimeError


def test_list_subjects():

    cfg = config()

    layout = get_dataset_layout(pybids_test_dataset())

    subjects = list_subjects(layout, cfg)
    assert len(subjects) == 5

    cfg["participant"] = ["02"]
    subjects = list_subjects(layout, cfg)
    assert subjects == ["02"]


def test_get_dataset_layout_smoke_test():
    get_dataset_layout(Path("data"))

    shutil.rmtree("data")


def test_get_deepmreye_filename():

    layout = get_dataset_layout(pybids_test_dataset())

    output_file = Path(get_test_data_path()).joinpath(
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
