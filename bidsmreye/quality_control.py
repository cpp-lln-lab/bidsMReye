"""TODO."""
from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from bids import BIDSLayout  # type: ignore

from bidsmreye.utils import check_layout
from bidsmreye.utils import Config
from bidsmreye.utils import create_bidsname
from bidsmreye.utils import get_dataset_layout
from bidsmreye.utils import list_subjects
from bidsmreye.utils import set_this_filter

log = logging.getLogger("bidsmreye")


def perform_quality_control(layout: BIDSLayout, confounds_tsv: str | Path) -> None:
    """Perform quality control on the confounds.

    :param layout: pybids layout to of the dataset to act on.
    :type layout: BIDSLayout

    :param confounds_tsv: Path to the confounds TSV file.
    :type confounds_tsv: str | Path
    """
    confounds_tsv = Path(confounds_tsv)
    confounds = pd.read_csv(confounds_tsv, sep="\t")

    nb_timepoints = confounds.shape[0]

    repetition_time = get_repetition_time(layout, confounds_tsv)

    eye_timestamp = np.arange(0, repetition_time * nb_timepoints, repetition_time)
    confounds["eye_timestamp"] = eye_timestamp

    cols = confounds.columns.tolist()
    cols.insert(0, cols.pop(cols.index("eye_timestamp")))
    confounds = confounds[cols]

    confounds.to_csv(confounds_tsv, sep="\t", index=False)


def get_repetition_time(layout: BIDSLayout, file: str | Path) -> float | None:
    """Get the repetition time from the sidecar JSON file."""
    repetition_time = None

    sidecar_name = create_bidsname(layout, file, "confounds_json")

    if sidecar_name.is_file():
        with open(sidecar_name) as f:
            content = json.load(f)
            SamplingFrequency = content.get("SamplingFrequency", None)
            if SamplingFrequency is not None and SamplingFrequency > 0:
                repetition_time = 1 / SamplingFrequency

    return repetition_time


def quality_control(cfg: Config) -> None:
    """Run quality control on the output dataset."""

    log.info("QUALITY CONTROL")

    layout_out = get_dataset_layout(cfg.output_folder)
    check_layout(cfg, layout_out)

    subjects = list_subjects(cfg, layout_out)

    for subject_label in subjects:

        qc_subject(cfg, layout_out, subject_label)


def qc_subject(cfg: Config, layout_out: BIDSLayout, subject_label: str) -> None:
    """Run quality control for one subject."""

    log.info(f"Running subject: {subject_label}")

    this_filter = set_this_filter(cfg, subject_label, "eyetrack")

    data = layout_out.get(
        return_type="filename",
        regex_search=True,
        **this_filter,
    )

    to_print = [str(Path(x).relative_to(layout_out.root)) for x in data]
    log.debug(f"Found files\n{to_print}")

    for file in data:

        perform_quality_control(layout_out, file)
