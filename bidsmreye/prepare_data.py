"""Run coregistration and extract data."""
import logging

from bids import BIDSLayout  # type: ignore
from deepmreye import preprocess  # type: ignore

from bidsmreye.bidsutils import check_layout
from bidsmreye.bidsutils import create_bidsname
from bidsmreye.bidsutils import get_bids_filter_config
from bidsmreye.bidsutils import get_dataset_layout
from bidsmreye.bidsutils import set_dataset_description
from bidsmreye.bidsutils import write_dataset_description
from bidsmreye.methods import methods
from bidsmreye.utils import Config
from bidsmreye.utils import create_dir_if_absent
from bidsmreye.utils import get_deepmreye_filename
from bidsmreye.utils import list_subjects
from bidsmreye.utils import move_file
from bidsmreye.utils import return_regex

log = logging.getLogger("rich")


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

    preprocess.run_participant(
        img, dme_template, eyemask_big, eyemask_small, x_edges, y_edges, z_edges
    )


def preprocess_subject(
    cfg: Config, layout_in: BIDSLayout, layout_out: BIDSLayout, subject_label: str
) -> None:
    """Run coregistration and extract data for one subject.

    Args:
        layout_in (BIDSLayout): Layout input dataset.
        layout_out (BIDSLayout): Layout output dataset.
        subject_label (str): Can be a regular expression.
    """
    log.info(f"Running subject: {subject_label}")

    this_filter = get_bids_filter_config()["bold"]
    this_filter["suffix"] = return_regex(this_filter["suffix"])
    this_filter["task"] = return_regex(cfg.task)
    this_filter["space"] = return_regex(cfg.space)
    this_filter["subject"] = subject_label

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

        mask_name = create_bidsname(layout_out, img, "mask")
        deepmreye_mask_name = get_deepmreye_filename(layout_in, img, "mask")
        move_file(deepmreye_mask_name, mask_name)

        report_name = create_bidsname(layout_out, img, "report")
        deepmreye_mask_report = get_deepmreye_filename(layout_in, img, "report")
        move_file(deepmreye_mask_report, report_name)


def prepare_data(cfg: Config) -> None:
    """Run coregistration and extract data for all subjects.

    :param cfg: Configuration object
    :type cfg: Config
    """
    layout_in = get_dataset_layout(cfg.input_folder)
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

        preprocess_subject(cfg, layout_in, layout_out, subject_label)
