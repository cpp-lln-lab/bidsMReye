"""TODO."""
import logging
import warnings
from pathlib import Path

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
from bidsmreye.utils import list_subjects
from bidsmreye.utils import move_file
from bidsmreye.utils import return_regex

log = logging.getLogger("rich")


def convert_confounds(cfg: dict, layout_out: BIDSLayout, subject_label: str):
    """Convert numpy output to TSV.

    Args:
        cfg (dict): configuration dictionary

        layout_out (_type_): pybids layout to of the dataset to act on.

        subject_label (str): The label(s) of the participant(s) that should be analyzed.
    """
    entities = {"subject": subject_label, "task": cfg["task"], "space": cfg["space"]}
    confound_numpy = create_bidsname(layout_out, entities, "confounds_numpy")

    content = np.load(
        file=confound_numpy,
        allow_pickle=True,
    )

    evaluation = content.item(0)

    for key, item in evaluation.items():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            this_pred = np.nanmedian(item["pred_y"], axis=1)

        confound_name = create_bidsname(layout_out, key + "p", "confounds_tsv")

        log.info(f"Saving to {confound_name}")

        pd.DataFrame(this_pred).to_csv(
            confound_name, sep="\t", header=["x_position", "y_position"], index=None
        )


def generalize(cfg: dict) -> None:
    """Apply model weights to new data.

    Args:
        cfg (dict): configuration dictionary
    """
    output_dataset_path = cfg["output_folder"]

    layout_out = get_dataset_layout(output_dataset_path)
    check_layout(layout_out)

    subjects = list_subjects(layout_out, cfg)

    all_data = []

    for subject_label in subjects:

        data = layout_out.get(
            return_type="filename",
            subject=return_regex(subject_label),
            suffix="^bidsmreye$",
            task=return_regex(cfg["task"]),
            space=return_regex(cfg["space"]),
            extension=".npz",
            regex_search=True,
        )

        for file in data:
            log.info(f"adding file: {Path(file).name}")
            all_data.append(file)

        print("\n")
        generators = data_generator.create_generators(all_data, all_data)
        generators = (*generators, all_data, all_data)
        print("\n")

        # Get untrained model and load with trained weights
        opts = model_opts.get_opts()
        model_weights = cfg["model_weights_file"]

        (model, model_inference) = train.train_model(
            dataset="example_data",
            generators=generators,
            opts=opts,
            return_untrained=True,
        )
        model_inference.load_weights(model_weights)

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

        # TODO save figure
        fig = analyse.visualise_predictions_slider(
            evaluation,
            scores,
            color="rgb(0, 150, 175)",
            bg_color="rgb(255,255,255)",
            ylim=[-11, 11],
        )
        print(log.level)
        if log.level in ["DEBUG", "INFO"]:
            fig.show()

        entities = {"subject": subject_label, "task": cfg["task"], "space": cfg["space"]}
        confound_numpy = create_bidsname(layout_out, entities, "confounds_numpy")
        source_file = Path(layout_out.root).joinpath(
            f"sub-{subject_label}", "func", "results_tmp.npy"
        )
        move_file(
            source_file,
            confound_numpy,
        )

        convert_confounds(cfg, layout_out, subject_label)
