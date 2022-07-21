"""foo."""
import os
import warnings

import numpy as np
import pandas as pd
from rich import print

from bidsmreye.bidsutils import check_layout
from bidsmreye.bidsutils import create_bidsname
from bidsmreye.bidsutils import get_dataset_layout


def generate_confounds(cfg):
    """Convert results saved as numpy array to a one TSV per subject."""
    dataset_path = cfg["output_folder"]

    print(f"\nindexing {dataset_path}\n")

    layout = get_dataset_layout(dataset_path)
    check_layout(layout)

    content = np.load(
        file=os.path.join(dataset_path, "bidsmreyeresults_group_output.npy"),
        allow_pickle=True,
    )

    evaluation = content.item(0)

    for key, item in evaluation.items():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            this_pred = np.nanmedian(item["pred_y"], axis=1)

        confound_name = create_bidsname(layout, key + "p", "confounds")

        print(f"Saving to {confound_name} \n")

        pd.DataFrame(this_pred).to_csv(
            confound_name, sep="\t", header=["x_position", "y_position"], index=None
        )
