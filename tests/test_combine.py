from pathlib import Path

from bids.tests import get_test_data_path

from bidsmreye.combine import combine
from bidsmreye.utils import Config


def pybids_test_dataset():
    return Path(get_test_data_path()).joinpath("synthetic", "derivatives", "fmriprep")


def test_combine_smoke():

    output_location = Path().resolve()
    output_location = output_location.joinpath("tests", "data")

    cfg = Config(
        pybids_test_dataset(),
        output_location,
    )

    combine(cfg)

    output_location.joinpath(
        "sub-01",
        "func",
        "sub-01_task-nback_space-MNI152NLin2009cAsym_desc-nolabel_bidsmreye.npz",
    ).unlink
