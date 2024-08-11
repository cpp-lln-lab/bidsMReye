from __future__ import annotations

import json

from bidsmreye.bids_utils import get_dataset_layout
from bidsmreye.generalize import convert_confounds


def test_convert_confounds(output_dir):
    layout_out = get_dataset_layout(output_dir)

    file = (
        output_dir
        / "sub-01"
        / "func"
        / "sub-01_task-nback_space-MNI152NLin2009cAsym_desc-1to6_confounds.npy"
    )
    file.parent.mkdir(parents=True, exist_ok=True)
    with open(file.with_suffix(".json"), "w") as f:
        json.dump({"SamplingFrequency": 2.0}, f)

    confound_name = convert_confounds(layout_out, file)

    assert confound_name.is_file()
