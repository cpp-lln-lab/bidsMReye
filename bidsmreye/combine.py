"""foo."""
import os
import pickle
import warnings

import numpy as np
from bidsname import create_bidsname
from deepmreye import preprocess
from rich import print
from utils import check_layout
from utils import config
from utils import get_dataset_layout
from utils import list_subjects
from utils import move_file
from utils import return_regex


def process_subject(layout, subject_label):
    """_summary_.

    Args:
        layout (_type_): _description_
        subject_label (_type_): _description_
    """
    cfg = config()

    # TODO performance: do not reload the input layout for every subject
    layout = get_dataset_layout(cfg["output_folder"])

    print(f"Running subject: {subject_label}")

    masks = layout.get(
        return_type="filename",
        subject=return_regex(subject_label),
        suffix="^mask$",
        task=return_regex(cfg["task"]),
        space=return_regex(cfg["space"]),
        extension=".p",
        regex_search=True,
    )

    for i, img in enumerate(masks):

        print(f"Input mask: {img}")

        # Load mask and normalize it
        this_mask = pickle.load(open(img, "rb"))
        this_mask = preprocess.normalize_img(this_mask)

        # If experiment has no labels use dummy labels
        # 10 is the number of subTRs used in the pretrained weights, 2 is XY
        this_label = np.zeros((this_mask.shape[3], 10, 2))

        # Check if each functional image has a corresponding label.
        # Note that mask has time as third dimension
        if this_mask.shape[3] != this_label.shape[0]:
            warnings.warns(
                f"""
                Skipping file {img} from subject {subject_label}\n
                Wrong alignment (Mask {this_mask.shape} - Label {this_label.shape}
                """
            )
            continue

        # Store for each runs
        subj = {"data": [], "labels": [], "ids": []}
        subj["data"].append(this_mask)
        subj["labels"].append(this_label)
        subj["ids"].append(
            ([subject_label] * this_label.shape[0], [i] * this_label.shape[0])
        )

        save_participant_file(layout, img, subj)


def save_participant_file(layout, img, subj):
    """_summary_.

    Args:
        layout (_type_): _description_
        img (_type_): _description_
        subj (_type_): _description_
    """
    output_file = create_bidsname(layout, img, "no_label")

    preprocess.save_data(
        os.path.basename(output_file),
        subj["data"],
        subj["labels"],
        subj["ids"],
        layout.root,
        center_labels=False,
    )

    file_to_move = os.path.join(
        layout.root, "..", f"deepMReye{os.path.basename(output_file)}"
    )

    move_file(file_to_move, output_file)


def combine():
    """_summary_."""
    # add labels to dataset
    cfg = config()

    dataset_path = cfg["output_folder"]

    print(f"\nindexing {dataset_path}\n")

    layout = get_dataset_layout(dataset_path)
    check_layout(layout)

    subjects = list_subjects(layout, cfg)
    if cfg["debug"]:
        subjects = [subjects[0]]

    print(f"processing subjects: {subjects}\n")

    for subject_label in subjects:

        process_subject(layout, subject_label)
