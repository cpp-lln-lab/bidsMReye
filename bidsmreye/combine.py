"""TODO."""
import logging
import pickle
import warnings
from pathlib import Path

import numpy as np  # type: ignore
from bids import BIDSLayout  # type: ignore
from deepmreye import preprocess  # type: ignore

from bidsmreye.utils import check_layout
from bidsmreye.utils import Config
from bidsmreye.utils import create_bidsname
from bidsmreye.utils import get_bids_filter_config
from bidsmreye.utils import get_dataset_layout
from bidsmreye.utils import list_subjects
from bidsmreye.utils import move_file
from bidsmreye.utils import return_regex

log = logging.getLogger("rich")


def process_subject(cfg: Config, layout_out: BIDSLayout, subject_label: str):
    """Process subject.

    :param cfg: Configuration object.
    :type cfg: Config

    :param layout_out: Output dataset layout.
    :type layout_out: BIDSLayout

    :param subject_label: Can be a regular expression.
    :type subject_label: str
    """
    log.info(f"Running subject: {subject_label}")

    this_filter = get_bids_filter_config()["mask"]
    this_filter["suffix"] = return_regex(this_filter["suffix"])
    this_filter["task"] = return_regex(cfg.task)
    this_filter["space"] = return_regex(cfg.space)
    this_filter["subject"] = subject_label
    if cfg.run:
        this_filter["run"] = return_regex(cfg.run)

    log.debug(f"Looking for files with filter\n{this_filter}")

    masks = layout_out.get(return_type="filename", regex_search=True, **this_filter)

    log.debug(f"Found files\n{masks}")

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
    """Save participant file.

    :param layout_out: Output dataset layout.
    :type layout_out: BIDSLayout

    :param img: _description_
    :type img: _type_

    :param subj: _description_
    :type subj: dict
    """
    output_file = create_bidsname(layout_out, Path(img), "no_label")

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


def combine(cfg: Config):
    """Add labels to dataset.

    :param cfg: Configuration object.
    :type cfg: Config
    """
    layout_out = get_dataset_layout(cfg.output_folder)
    check_layout(cfg, layout_out)

    subjects = list_subjects(cfg, layout_out)

    for subject_label in subjects:

        process_subject(cfg, layout_out, subject_label)
