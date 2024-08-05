"""Run coregistration and extract data from eye masks in MNI space."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import numpy as np
from bids import BIDSLayout  # type: ignore
from bids.layout import BIDSFile
from deepmreye import preprocess

from bidsmreye.bids_utils import (
    check_layout,
    create_bidsname,
    get_dataset_layout,
    init_dataset,
    list_subjects,
    save_sampling_frequency_to_json,
)
from bidsmreye.configuration import Config
from bidsmreye.logging import bidsmreye_log
from bidsmreye.utils import (
    check_if_file_found,
    get_deepmreye_filename,
    move_file,
    progress_bar,
    set_this_filter,
)

log = bidsmreye_log(name="bidsmreye")


def coregister_and_extract_data(img: str, non_linear_coreg: bool = False) -> None:
    """Coregister image to eye template and extract data from eye mask for one image.

    :param img: Image to coregister and extract data from
    :type img: str
    """
    (
        eyemask_small,
        eyemask_big,
        dme_template,
        _,
        x_edges,
        y_edges,
        z_edges,
    ) = preprocess.get_masks()

    transforms = ["Affine", "Affine", "SyNAggro"] if non_linear_coreg else None

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


def combine_data_with_empty_labels(layout_out: BIDSLayout, img: Path, i: int = 1) -> Path:
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
    log.debug(f"Combining data with empty labels: {img}")

    # Load data and normalize it
    data = pickle.load(open(img, "rb"))
    data = preprocess.normalize_img(data)

    # If experiment has no labels use dummy labels
    # 10 is the number of subTRs used in the pretrained weights, 2 is XY
    labels = np.zeros((data.shape[3], 10, 2))

    entities = layout_out.parse_file_entities(img)

    # Store for each runs
    subj: dict[str, list[Any]] = {"data": [], "labels": [], "ids": []}
    subj["data"].append(data)
    subj["labels"].append(labels)
    subj["ids"].append(([entities["subject"]] * labels.shape[0], [i] * labels.shape[0]))

    output_file = create_bidsname(layout_out, Path(img), "no_label")
    file_to_move = Path(layout_out.root) / ".." / "bidsmreye" / output_file.name

    preprocess.save_data(
        output_file.name,
        subj["data"],
        subj["labels"],
        subj["ids"],
        layout_out.root,
        center_labels=False,
    )

    return file_to_move


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

    this_filter = set_this_filter(cfg, subject_label, "bold")

    bf = layout_in.get(
        regex_search=True,
        **this_filter,
    )

    check_if_file_found(bf, this_filter, layout_in)

    for img in bf:
        prepapre_image(cfg, layout_in, layout_out, img)


def prepapre_image(
    cfg: Config, layout_in: BIDSLayout, layout_out: BIDSLayout, img: BIDSFile
) -> None:
    """Preprocess a single functional image."""
    img_path = img.path

    report_name = create_bidsname(layout_out, filename=img_path, filetype="report")
    mask_name = create_bidsname(layout_out, filename=img_path, filetype="mask")
    output_file = create_bidsname(layout_out, Path(img_path), "no_label")

    if (
        not cfg.force
        and report_name.exists()
        and mask_name.exists()
        and output_file.exists()
    ):
        log.debug(
            "Output for the following file already exists. "
            "Use the '--force' option to overwrite. "
            f"\n '{Path(img_path).name}'"
        )
        return

    log.info(f"Processing file: {Path(img_path).name}")

    coregister_and_extract_data(img_path, non_linear_coreg=cfg.non_linear_coreg)

    deepmreye_mask_report = get_deepmreye_filename(
        layout_in, img=img_path, filetype="report"
    )
    move_file(deepmreye_mask_report, report_name)

    deepmreye_mask_name = get_deepmreye_filename(layout_in, img=img_path, filetype="mask")
    move_file(deepmreye_mask_name, mask_name)

    source = str(Path(img_path).relative_to(layout_in.root))
    save_sampling_frequency_to_json(layout_out, img=img, source=source)

    combine_data_with_empty_labels(layout_out, mask_name)
    file_to_move = Path(layout_out.root) / ".." / "bidsmreye" / output_file.name
    move_file(file_to_move, output_file)


def prepare_data(cfg: Config) -> None:
    """Run coregistration and extract data for all subjects.

    :param cfg: Configuration object
    :type cfg: Config
    """
    layout_in = get_dataset_layout(
        cfg.input_dir,
        use_database=True,
        config=["bids", "derivatives"],
        reset_database=cfg.reset_database,
    )
    check_layout(cfg, layout_in)

    layout_out = init_dataset(cfg)

    subjects = list_subjects(cfg, layout_in)

    text = "PREPARING DATA"
    if cfg.non_linear_coreg:
        log.info("Using non-linear coregistration")

    with progress_bar(text=text) as progress:
        subject_loop = progress.add_task(
            description="processing subject", total=len(subjects)
        )
        for subject_label in subjects:
            process_subject(cfg, layout_in, layout_out, subject_label)
            progress.update(subject_loop, advance=1)
