"""Run coregistration and extract data."""
import logging
import pickle
from pathlib import Path

import numpy as np  # type: ignore
from bids import BIDSLayout  # type: ignore
from deepmreye import preprocess  # type: ignore

from bidsmreye.methods import methods
from bidsmreye.utils import check_layout
from bidsmreye.utils import Config
from bidsmreye.utils import create_bidsname
from bidsmreye.utils import create_dir_if_absent
from bidsmreye.utils import get_dataset_layout
from bidsmreye.utils import get_deepmreye_filename
from bidsmreye.utils import list_subjects
from bidsmreye.utils import move_file
from bidsmreye.utils import return_regex
from bidsmreye.utils import set_dataset_description
from bidsmreye.utils import write_dataset_description


log = logging.getLogger("bidsmreye")


def coregister_and_extract_data(img: str) -> None:
    """Coregister image to eye template and extract data from eye mask for one image.

    :param img: Image to coregister and extract data from
    :type img: str
    """
    (
        eyemask_small,
        eyemask_big,
        dme_template,
        mask,
        x_edges,
        y_edges,
        z_edges,
    ) = preprocess.get_masks()

    transforms = None
    # if Affine:
    #     transforms = ["Affine", "Affine", "SyNAggro"]

    preprocess.run_participant(
        img,
        dme_template,
        eyemask_big,
        eyemask_small,
        x_edges,
        y_edges,
        z_edges,
        transforms=transforms,
    )


def combine_data_with_empty_labels(layout_out, subject_label, img, i=1):
    """Combine data with empty labels.

    :param layout_out: _description_
    :type layout_out: _type_
    :param subject_label: _description_
    :type subject_label: _type_
    :param img: _description_
    :type img: _type_
    :param i: _description_, defaults to 1
    :type i: int, optional
    """
    log.info(f"Combining data with empty labesl: {img}")

    # Load mask and normalize it
    this_mask = pickle.load(open(img, "rb"))
    this_mask = preprocess.normalize_img(this_mask)

    # If experiment has no labels use dummy labels
    # 10 is the number of subTRs used in the pretrained weights, 2 is XY
    this_label = np.zeros((this_mask.shape[3], 10, 2))

    # Store for each runs
    subj = {"data": [], "labels": [], "ids": []}  # type: dict
    subj["data"].append(this_mask)
    subj["labels"].append(this_label)
    subj["ids"].append(([subject_label] * this_label.shape[0], [i] * this_label.shape[0]))

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


def process_subject(
    cfg: Config, layout_in: BIDSLayout, layout_out: BIDSLayout, subject_label: str
) -> None:
    """Run coregistration and extract data for one subject.

    :param cfg: Configuration object.
    :type cfg: Config

    :param layout_in: Layout input dataset.
    :type layout_in: BIDSLayout

    :param layout_out: Layout output dataset.
    :type layout_out: BIDSLayout

    :param subject_label: Can be a regular expression.
    :type subject_label: str
    """
    log.info(f"Running subject: {subject_label}")

    this_filter = cfg.bids_filter["bold"]
    this_filter["suffix"] = return_regex(this_filter["suffix"])
    this_filter["task"] = return_regex(cfg.task)
    this_filter["space"] = return_regex(cfg.space)
    this_filter["subject"] = subject_label
    if cfg.run:
        this_filter["run"] = return_regex(cfg.run)

    log.debug(f"Looking for files with filter\n{this_filter}")

    bf = layout_in.get(
        return_type="filename",
        regex_search=True,
        **this_filter,
    )

    log.debug(f"Found files\n{bf}")

    for img in bf:

        log.info(f"Processing {img}")

        coregister_and_extract_data(img)

        report_name = create_bidsname(layout_out, img, "report")
        deepmreye_mask_report = get_deepmreye_filename(layout_in, img, "report")
        move_file(deepmreye_mask_report, report_name)

        mask_name = create_bidsname(layout_out, img, "mask")
        deepmreye_mask_name = get_deepmreye_filename(layout_in, img, "mask")
        move_file(deepmreye_mask_name, mask_name)

        combine_data_with_empty_labels(layout_out, subject_label, mask_name)


def prepare_data(cfg: Config) -> None:
    """Run coregistration and extract data for all subjects.

    :param cfg: Configuration object
    :type cfg: Config
    """
    log.info("PREPARING DATA")

    layout_in = get_dataset_layout(cfg.input_folder, use_database=True)
    check_layout(cfg, layout_in)

    create_dir_if_absent(cfg.output_folder)
    layout_out = get_dataset_layout(cfg.output_folder)
    layout_out = set_dataset_description(layout_out)
    layout_out.dataset_description["DatasetType"] = "derivative"
    layout_out.dataset_description["GeneratedBy"][0]["Name"] = "bidsmreye"
    write_dataset_description(layout_out)

    citation_file = methods(cfg.output_folder)
    log.info(f"Method section generated: {citation_file}")

    subjects = list_subjects(cfg, layout_in)

    for subject_label in subjects:

        process_subject(cfg, layout_in, layout_out, subject_label)
