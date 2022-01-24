import os
import warnings

import numpy as np
import pandas as pd
from bidsname import create_bidsname
from rich import print
from utils import check_layout
from utils import config
from utils import get_dataset_layout


def generate_confounds():

    cfg = config()

    dataset_path = cfg["output_folder"]

    print(f"\nindexing {dataset_path}\n")

    layout = get_dataset_layout(dataset_path)
    check_layout(layout)

    content = np.load(
        file=os.path.join(dataset_path, "deepMReyeresults_group_output.npy"),
        allow_pickle=True,
    )

    evaluation = content.item(0)

    all_data = []

    subTR = False

    for key, item in evaluation.items():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if subTR:
                this_pred = np.reshape(
                    item["pred_y"],
                    (item["pred_y"].shape[0] * item["pred_y"].shape[1], -1),
                )
            else:
                this_pred = np.nanmedian(item["pred_y"], axis=1)
        confound_name = create_bidsname(layout, key + "p", "confounds")

        print(f"Saving to {confound_name} \n")

        pd.DataFrame(this_pred).to_csv(
            confound_name, sep="\t", header=["x_position", "y_position"], index=None
        )
