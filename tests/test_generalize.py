import os
from pathlib import Path

from bidsmreye.bidsutils import get_dataset_layout
from bidsmreye.generalize import convert_confounds


def test_convert_confounds():

    output_location = Path().resolve()
    output_location = Path.joinpath(output_location, "tests", "data", "bidsmreye")

    cfg = {
        "output_folder": output_location,
        "debug": False,
        "participant": [],
        "task": "auditory",
        "space": "MNI152NLin6Asym",
    }

    layout_out = get_dataset_layout(output_location)

    subject_label = "01"

    convert_confounds(cfg, layout_out, subject_label)

    os.remove(
        Path.joinpath(
            output_location,
            "sub-01",
            "func",
            "sub-01_task-auditory_space-MNI152NLin6Asym_desc-bidsmreye_timeseries.tsv",
        )
    )
