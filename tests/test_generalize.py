from __future__ import annotations

import shutil
from pathlib import Path

from bidsmreye.generalize import convert_confounds
from bidsmreye.utils import get_dataset_layout


def test_convert_confounds():

    output_location = Path().resolve()
    output_location = output_location.joinpath("tests", "data", "bidsmreye")

    layout_out = get_dataset_layout(output_location)

    file = output_location.joinpath(
        "sub-01",
        "func",
        "sub-01_task-nback_space-MNI152NLin2009cAsym_desc-bidsmreye_confounds.npy",
    )
    shutil.copy(file, file.with_suffix(".bak"))

    confound_name = convert_confounds(layout_out, file)

    assert confound_name.is_file()

    confound_name.unlink()
    shutil.copy(file.with_suffix(".bak"), file)
    file.with_suffix(".bak").unlink()
