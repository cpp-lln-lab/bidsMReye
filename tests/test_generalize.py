from pathlib import Path

from bids.tests import get_test_data_path

from bidsmreye.bidsutils import get_dataset_layout
from bidsmreye.generalize import convert_confounds
from bidsmreye.utils import Config


def pybids_test_dataset():
    return Path(get_test_data_path()).joinpath("synthetic", "derivatives", "fmriprep")


def test_convert_confounds():

    output_location = Path().resolve()
    output_location = output_location.joinpath("tests", "data")

    cfg = Config(
        pybids_test_dataset(),
        output_location,
        task=["nback"],
        space=["MNI152NLin2009cAsym"],
    )

    layout_out = get_dataset_layout(cfg.output_folder)

    subject_label = "01"

    convert_confounds(cfg, layout_out, subject_label)

    # TODO the task and space in this filename are different from the config
    # name because the filename is generated from the keys in the .npz file
    # no comment
    Path(cfg.output_folder).joinpath(
        "sub-01",
        "func",
        "sub-01_task-auditory_space-MNI152NLin6Asym_desc-bidsmreye_timeseries.tsv",
    ).unlink()
