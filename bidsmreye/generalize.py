"""TODO."""
import logging
import warnings
from pathlib import Path
from typing import Union

import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from bids import BIDSLayout  # type: ignore
from deepmreye import analyse  # type: ignore
from deepmreye import train
from deepmreye.util import data_generator  # type: ignore
from deepmreye.util import model_opts
from rich import print

from bidsmreye.utils import check_layout
from bidsmreye.utils import Config
from bidsmreye.utils import create_bidsname
from bidsmreye.utils import create_dir_for_file
from bidsmreye.utils import get_dataset_layout
from bidsmreye.utils import list_subjects
from bidsmreye.utils import move_file
from bidsmreye.utils import return_regex

log = logging.getLogger("bidsmreye")


def convert_confounds(layout_out: BIDSLayout, file: Union[str, Path]) -> Path:
    """Convert numpy output to TSV.

    :param layout_out: pybids layout to of the dataset to act on.
    :type layout_out: BIDSLayout

    :param file: File to generate the confounds for.
    :type file: Union[str, Path]

    :return: Name of the file generated.
    :rtype: Path

    This function should preferably work on a single file
    but should still be able to unpack the results from a numpy file
    with results from multiple files.
    """
    confound_numpy = create_bidsname(layout_out, file, "confounds_numpy")

    content = np.load(
        file=confound_numpy,
        allow_pickle=True,
    )

    evaluation = content.item(0)

    for key, item in evaluation.items():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            this_pred = np.nanmedian(item["pred_y"], axis=1)

        confound_name = create_bidsname(layout_out, Path(key + "p"), "confounds_tsv")

        log.info(f"Saving to {confound_name}")

        pd.DataFrame(this_pred).to_csv(
            confound_name, sep="\t", header=["x_position", "y_position"], index=None
        )

    return confound_name


def create_and_save_figure(layout_out: BIDSLayout, file: str, evaluation, scores):
    """Generate a figure for the eye motion timeseries.

    :param layout_out: Output dataset layout.
    :type  layout_out: BIDSLayout

    :param file:
    :type  file: str

    :param evaluation: see ``deepmreye.train.evaluate_model``
    :type  evaluation: _type_

    :param scores: see ``deepmreye.train.evaluate_model``
    :type  scores: _type_
    """
    fig = analyse.visualise_predictions_slider(
        evaluation,
        scores,
        color="rgb(0, 150, 175)",
        bg_color="rgb(255,255,255)",
        ylim=[-11, 11],
    )
    if log.isEnabledFor(logging.DEBUG):
        fig.show()

    confound_svg = create_bidsname(layout_out, file, "confounds_svg")
    create_dir_for_file(confound_svg)
    fig.write_image(confound_svg)


def create_confounds_tsv(layout_out: BIDSLayout, file: str, subject_label: str):
    """Generate a TSV file for the eye motion timeseries.

    :param layout_out:
    :type layout_out: BIDSLayout

    :param file:
    :type file: str

    :param subject_label:
    :type subject_label: str
    """
    confound_numpy = create_bidsname(layout_out, file, "confounds_numpy")

    source_file = Path(layout_out.root).joinpath(
        f"sub-{subject_label}", "results_tmp.npy"
    )

    move_file(
        source_file,
        confound_numpy,
    )

    convert_confounds(layout_out, file)


def process_subject(cfg: Config, layout_out: BIDSLayout, subject_label: str):
    """Run generalize for one subject.

    :param cfg: Configuration object
    :type cfg: Config

    :param layout_out:
    :type layout_out: BIDSLayout

    :param subject_label:
    :type subject_label: str
    """
    this_filter = cfg.bids_filter["no_label"]
    this_filter["suffix"] = return_regex(this_filter["suffix"])
    this_filter["task"] = return_regex(cfg.task)
    this_filter["space"] = return_regex(cfg.space)
    this_filter["subject"] = subject_label
    if cfg.run:
        this_filter["run"] = return_regex(cfg.run)

    log.debug(f"Looking for files with filter\n{this_filter}")

    data = layout_out.get(
        return_type="filename",
        regex_search=True,
        **this_filter,
    )

    log.debug(f"Found files\n{data}")

    for file in data:

        log.info(f"Processing file: {Path(file).name}")

        print("\n")
        generators = data_generator.create_generators([file], [file])
        generators = (*generators, [file], [file])
        print("\n")

        opts = model_opts.get_opts()

        (model, model_inference) = train.train_model(
            dataset="example_data",
            generators=generators,
            opts=opts,
            return_untrained=True,
        )
        model_inference.load_weights(cfg.model_weights_file)

        verbose = 0
        if log.isEnabledFor(logging.DEBUG):
            verbose = 2
        elif log.isEnabledFor(logging.INFO):
            verbose = 1

        (evaluation, scores) = train.evaluate_model(
            dataset="tmp",
            model=model_inference,
            generators=generators,
            save=True,
            model_path=f"{layout_out.root}/sub-{subject_label}/",
            model_description="",
            verbose=verbose,
            percentile_cut=80,
        )

        create_and_save_figure(layout_out, file, evaluation, scores)

        create_confounds_tsv(layout_out, file, subject_label)


def generalize(cfg: Config) -> None:
    """Apply model weights to new data.

    :param cfg: Configuration object
    :type cfg: Config
    """
    log.info("GENERALIZING")
    log.info(f"Using model: {cfg.model_weights_file}")

    layout_out = get_dataset_layout(cfg.output_folder)
    check_layout(cfg, layout_out)

    subjects = list_subjects(cfg, layout_out)

    for subject_label in subjects:

        process_subject(cfg, layout_out, subject_label)
