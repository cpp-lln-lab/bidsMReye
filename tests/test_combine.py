import os
from pathlib import Path

from bidsmreye.combine import combine


def test_combine_smoke():

    output_location = Path().resolve()
    output_location = Path.joinpath(output_location, "tests", "data", "bidsmreye")

    cfg = {
        "output_folder": output_location,
        "debug": False,
        "participant": [],
        "task": "auditory",
        "space": "MNI152NLin6Asym",
    }

    combine(cfg)

    os.remove(
        Path.joinpath(
            output_location,
            "sub-01",
            "func",
            "sub-01_task-auditory_space-MNI152NLin6Asym_desc-nolabel_bidsmreye.npz",
        )
    )
