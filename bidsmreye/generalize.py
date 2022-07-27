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

from bidsmreye.bidsutils import check_layout
from bidsmreye.bidsutils import create_bidsname
from bidsmreye.bidsutils import get_dataset_layout
from bidsmreye.utils import Config
from bidsmreye.utils import create_dir_for_file
from bidsmreye.utils import list_subjects
from bidsmreye.utils import move_file
from bidsmreye.utils import return_regex

log = logging.getLogger("rich")


def convert_confounds(layout_out: BIDSLayout, file: Union[str, Path]) -> Path:
    """Convert numpy output to TSV.

    Args:
        cfg (Config): configuration object

        layout_out (_type_): pybids layout to of the dataset to act on.

        subject_label (str): The label(s) of the participant(s) that should be analyzed.
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

    fig = analyse.visualise_predictions_slider(
        evaluation,
        scores,
        color="rgb(0, 150, 175)",
        bg_color="rgb(255,255,255)",
        ylim=[-11, 11],
    )
    if log.isEnabledFor(logging.DEBUG) or log.isEnabledFor(logging.INFO):
        fig.show()

    confound_svg = create_bidsname(layout_out, file, "confounds_svg")
    create_dir_for_file(confound_svg)
    fig.write_image(confound_svg)


def create_confounds_tsv(layout_out: BIDSLayout, file: str, subject_label: str):
    confound_numpy = create_bidsname(layout_out, file, "confounds_numpy")

    source_file = Path(layout_out.root).joinpath(
        f"sub-{subject_label}", "func", "results_tmp.npy"
    )

    move_file(
        source_file,
        confound_numpy,
    )

    convert_confounds(layout_out, file)


def generalize(cfg: Config) -> None:
    """Apply model weights to new data.

    Args:
        cfg (dict): configuration dictionary
    """
    layout_out = get_dataset_layout(cfg.output_folder)
    check_layout(cfg, layout_out)

    subjects = list_subjects(cfg, layout_out)

    for subject_label in subjects:

        this_filter = {
            "subject": return_regex(subject_label),
            "suffix": "^bidsmreye$",
            "task": return_regex(cfg.task),
            "space": return_regex(cfg.space),
            "extension": ".npz",
        }

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
                model_path=f"{layout_out.root}/sub-{subject_label}/func/",
                model_description="",
                verbose=verbose,
                percentile_cut=80,
            )

            create_and_save_figure(layout_out, file, evaluation, scores)

            create_confounds_tsv(layout_out, file, subject_label)
