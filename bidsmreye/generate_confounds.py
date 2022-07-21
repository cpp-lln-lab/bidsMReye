"""foo."""
import warnings

import numpy as np
import pandas as pd
from rich import print

from bidsmreye.bidsutils import check_layout
from bidsmreye.bidsutils import create_bidsname
from bidsmreye.bidsutils import get_dataset_layout
from bidsmreye.utils import list_subjects
from bidsmreye.utils import return_regex


def generate_confounds(cfg):
    """Convert results saved as numpy array to a one TSV per subject."""
    output_dataset_path = cfg["output_folder"]

    print(f"\nindexing {output_dataset_path}\n")

    layout_out = get_dataset_layout(output_dataset_path)
    check_layout(layout_out)

    subjects = list_subjects(layout_out, cfg)
    if cfg["debug"]:
        subjects = [subjects[0]]

    for subject_label in subjects:

        confound_numpy = layout_out.get(
            return_type="filename",
            subject=return_regex(subject_label),
            suffix="^confounds$",
            task=return_regex(cfg["task"]),
            space=return_regex(cfg["space"]),
            extension=".npy",
            regex_search=True,
        )

        # there should be only one file
        content = np.load(
            file=confound_numpy[0],
            allow_pickle=True,
        )

        evaluation = content.item(0)

        for key, item in evaluation.items():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                this_pred = np.nanmedian(item["pred_y"], axis=1)

            confound_name = create_bidsname(layout_out, key + "p", "confounds_tsv")

            print(f"Saving to {confound_name} \n")

            pd.DataFrame(this_pred).to_csv(
                confound_name, sep="\t", header=["x_position", "y_position"], index=None
            )
