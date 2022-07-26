"""TODO."""
import logging
import pickle
import warnings
from pathlib import Path

import numpy as np  # type: ignore
from bids import BIDSLayout  # type: ignore
from deepmreye import preprocess  # type: ignore

from bidsmreye.bidsutils import check_layout
from bidsmreye.bidsutils import create_bidsname
from bidsmreye.bidsutils import get_dataset_layout
from bidsmreye.utils import list_subjects
from bidsmreye.utils import move_file
from bidsmreye.utils import return_regex

log = logging.getLogger("rich")


def process_subject(cfg: dict, layout_out: BIDSLayout, subject_label: str):
    """_summary_.

    Args:
        layout_out (BIDSLayout): _description_

        subject_label (str): Can be a regular expression.
    """
    log.info(f"Running subject: {subject_label}")

    masks = layout_out.get(
        return_type="filename",
        subject=return_regex(subject_label),
        suffix="^mask$",
        task=return_regex(cfg["task"]),
        space=return_regex(cfg["space"]),
        extension=".p",
        regex_search=True,
    )

    for i, img in enumerate(masks):

        log.info(f"Input mask: {img}")

        # Load mask and normalize it
        this_mask = pickle.load(open(img, "rb"))
        this_mask = preprocess.normalize_img(this_mask)

        # If experiment has no labels use dummy labels
        # 10 is the number of subTRs used in the pretrained weights, 2 is XY
        this_label = np.zeros((this_mask.shape[3], 10, 2))

        # Check if each functional image has a corresponding label.
        # Note that mask has time as third dimension
        if this_mask.shape[3] != this_label.shape[0]:
            warnings.warn(
                f"""
                Skipping file {img} from subject {subject_label}\n
                Wrong alignment (Mask {this_mask.shape} - Label {this_label.shape}
                """
            )
            continue

        # Store for each runs
        subj = {"data": [], "labels": [], "ids": []}  # type: dict
        subj["data"].append(this_mask)
        subj["labels"].append(this_label)
        subj["ids"].append(
            ([subject_label] * this_label.shape[0], [i] * this_label.shape[0])
        )

        save_participant_file(layout_out, img, subj)


def save_participant_file(layout_out: BIDSLayout, img, subj: dict):
    """_summary_.

    Args:
        layout_out (BIDSLayout): _description_

        img (_type_): _description_

        subj (dict): _description_
    """
    output_file = create_bidsname(layout_out, img, "no_label")

    preprocess.save_data(
        output_file.name,
        subj["data"],
        subj["labels"],
        subj["ids"],
        layout_out.root,
        center_labels=False,
    )

    file_to_move = Path(layout_out.root).joinpath("..", "bidsmreye", output_file.name)

    move_file(file_to_move, output_file)


def combine(cfg: dict):
    """Add labels to dataset."""
    output_dataset_path = cfg["output_folder"]
    layout_out = get_dataset_layout(output_dataset_path)
    check_layout(layout_out)

    subjects = list_subjects(layout_out, cfg)

    for subject_label in subjects:

        process_subject(cfg, layout_out, subject_label)
