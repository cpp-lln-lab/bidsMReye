"""Tools to compute and plot quality controls at the file or group level."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from bids import BIDSLayout  # type: ignore
from scipy.stats.distributions import chi2

from bidsmreye.bids_utils import (
    check_layout,
    create_bidsname,
    get_dataset_layout,
    init_dataset,
    list_subjects,
    return_desc_entity,
)
from bidsmreye.configuration import Config
from bidsmreye.logger import bidsmreye_log
from bidsmreye.report import generate_report
from bidsmreye.utils import (
    add_timestamps_to_dataframe,
    check_if_file_found,
    create_dir_for_file,
    progress_bar,
    set_this_filter,
)
from bidsmreye.visualize import visualize_eye_gaze_data

log = bidsmreye_log("bidsmreye")


def compute_displacement(x: pd.Series, y: pd.Series) -> pd.Series:
    return np.sqrt((x.diff() ** 2) + (y.diff() ** 2))


def add_qc_to_sidecar(confounds: pd.DataFrame, sidecar_name: Path) -> None:
    """Add quality control metrics to the sidecar json file.

    :param layout: Layout of the BIDS dataset to which the confounds tsv file belongs to
    :type  layout: BIDSLayout

    :param confounds_tsv: path the the confounds tsv file
    :type  confounds_tsv: str | Path

    :return: Path to the sidecar json file
    :rtype: Path
    """
    log.info(f"Quality control data added to {sidecar_name}")

    if sidecar_name.exists():
        with open(sidecar_name) as f:
            content = json.load(f)
    # In case we are adding the metrics for a file that has its metadata
    # in the root of the dataset
    else:
        create_dir_for_file(file=sidecar_name)
        content = {}

    content["NbDisplacementOutliers"] = int(confounds["displacement_outliers"].sum())
    content["NbXOutliers"] = int(confounds["x_outliers"].sum())
    content["NbYOutliers"] = int(confounds["y_outliers"].sum())
    content["XVar"] = confounds["x_coordinate"].var()
    content["YVar"] = confounds["y_coordinate"].var()
    content["Columns"] = confounds.columns.to_list()

    content["displacement"] = {
        "Description": (
            "Framewise eye movement computed from the X and Y eye position "
            "between 2 consecutives timeframes."
        ),
        "Units": "degrees",
    }
    content["displacement_outliers"] = {
        "Description": (
            "Displacement outliers computed using robust ouliers with Carling's k."
        ),
        "Levels": {"0": "not an outlier", "1": "outlier"},
    }
    content["x_outliers"] = {
        "Description": (
            "X position outliers computed using robust ouliers with Carling's k."
        ),
        "Levels": {"0": "not an outlier", "1": "outlier"},
    }
    content["y_outliers"] = {
        "Description": (
            "Y position outliers computed using robust ouliers with Carling's k."
        ),
        "Levels": {"0": "not an outlier", "1": "outlier"},
    }

    content = {key: content[key] for key in sorted(content)}

    with open(sidecar_name, "w") as f:
        json.dump(content, f, indent=4)


def compute_displacement_and_outliers(confounds: pd.DataFrame) -> pd.DataFrame:
    confounds["displacement"] = compute_displacement(
        confounds["x_coordinate"], confounds["y_coordinate"]
    )

    confounds["displacement_outliers"] = compute_robust_outliers(
        confounds["displacement"], outlier_type="Carling"
    )

    confounds["x_outliers"] = compute_robust_outliers(
        confounds["x_coordinate"], outlier_type="Carling"
    )
    log.debug(f"Found {confounds['x_outliers'].sum()} x outliers")

    confounds["y_outliers"] = compute_robust_outliers(
        confounds["y_coordinate"], outlier_type="Carling"
    )
    log.debug(f"Found {confounds['y_outliers'].sum()} y outliers")

    return confounds


def perform_quality_control(
    cfg: Config,
    layout_in: BIDSLayout,
    confounds_tsv: str | Path,
    layout_out: BIDSLayout | None = None,
) -> None:
    """Perform quality control on the confounds.

    Compute displacement and outlier for a given eyetrack.tsv file
    and create a visualization for it that is saved as an html file.

    :param layout: pybids layout to of the dataset to act on.
    :type  layout: BIDSLayout

    :param confounds_tsv: Path to the confounds TSV file.
    :type  confounds_tsv: str | Path
    """
    if layout_out is None:
        layout_out = layout_in

    confounds_tsv = Path(confounds_tsv)
    visualization_html_file = create_bidsname(layout_out, confounds_tsv, "confounds_html")
    if not cfg.force and visualization_html_file.exists():
        log.debug(
            "Output for the following file already exists. "
            "Use the '--force' option to overwrite. "
            f"\n '{confounds_tsv.name}'"
        )
        return

    confounds = pd.read_csv(confounds_tsv, sep="\t")

    if "timestamp" not in confounds.columns:
        extra_entities = None
        if cfg.model_weights_file is not None:
            extra_entities = {"desc": return_desc_entity(Path(cfg.model_weights_file))}
        sampling_frequency = get_sampling_frequency(
            layout_in, confounds_tsv, extra_entities=extra_entities
        )

        if sampling_frequency is not None:
            confounds = add_timestamps_to_dataframe(confounds, sampling_frequency)

    compute_displacement_and_outliers(confounds)

    sidecar_name = create_bidsname(layout_out, confounds_tsv, "confounds_json")
    add_qc_to_sidecar(confounds, sidecar_name)

    fig = visualize_eye_gaze_data(confounds)
    fig.update_layout(showlegend=False, height=800)

    create_dir_for_file(visualization_html_file)
    fig.write_html(visualization_html_file)

    confounds_tsv = create_bidsname(layout_out, confounds_tsv, "confounds_tsv")
    confounds.to_csv(confounds_tsv, sep="\t", index=False)


def get_sampling_frequency(
    layout: BIDSLayout, file: str | Path, extra_entities: dict[str, str] | None = None
) -> float | None:
    """Get the sampling frequency from the sidecar JSON file."""
    sampling_frequency = None

    sidecar_name = create_bidsname(
        layout, file, "confounds_json", extra_entities=extra_entities
    )

    # TODO: deal with cases where the sidecar is in the root of the dataset
    if sidecar_name.is_file():
        with open(sidecar_name) as f:
            content = json.load(f)
            SamplingFrequency = content.get("SamplingFrequency", None)
            if SamplingFrequency is not None and SamplingFrequency > 0:
                sampling_frequency = SamplingFrequency
    else:
        log.error(
            "The following sidecar was not found. "
            f"Cannot infer sampling frequency.\n{sidecar_name}."
        )

    return sampling_frequency


def quality_control_output(cfg: Config) -> None:
    """Run quality control on the output dataset."""
    layout_out = get_dataset_layout(cfg.output_dir)
    check_layout(cfg, layout_out)

    subjects = list_subjects(cfg, layout_out)

    text = "QUALITY CONTROL"
    with progress_bar(text=text) as progress:
        subject_loop = progress.add_task(
            description="processing subject", total=len(subjects)
        )
        for subject_label in subjects:
            qc_subject(cfg, layout_out, subject_label)
            generate_report(
                output_dir=cfg.output_dir,
                subject_label=subject_label,
                action="generalize",
            )
            progress.update(subject_loop, advance=1)


def quality_control_input(cfg: Config) -> None:
    """Run quality control on the input dataset."""
    layout_in = get_dataset_layout(cfg.input_dir)
    check_layout(cfg, layout_in, "eyetrack")

    layout_out = init_dataset(cfg, qc_only=True)

    subjects = list_subjects(cfg, layout_in)

    text = "QUALITY CONTROL"
    with progress_bar(text=text) as progress:
        subject_loop = progress.add_task(
            description="processing subject", total=len(subjects)
        )
        for subject_label in subjects:
            qc_subject(cfg, layout_in, subject_label, layout_out)
            generate_report(
                output_dir=cfg.output_dir,
                subject_label=subject_label,
                action="generalize",
            )
            progress.update(subject_loop, advance=1)


def qc_subject(
    cfg: Config,
    layout_in: BIDSLayout,
    subject_label: str,
    layout_out: BIDSLayout | None = None,
) -> None:
    """Run quality control for one subject."""
    log.info(f"Running subject: {subject_label}")

    this_filter = set_this_filter(cfg, subject_label, "eyetrack")

    bf = layout_in.get(
        regex_search=True,
        **this_filter,
    )

    check_if_file_found(bf, this_filter, layout_in)

    for file in bf:
        perform_quality_control(cfg, layout_in, file.path, layout_out)


def compute_robust_outliers(
    time_series: pd.Series, outlier_type: str | None = None
) -> list[int] | type[NotImplementedError]:
    """Compute robust ouliers of a time series using S-outliers or Carling's k.

    :param series: Series to compute the outliers on.
    :type series: pd.Series

    :param outlier_type: Default to 'S-outliers'.
    :type outlier_type: str

    :return: Series of booleans indicating the outliers.
    :rtype: pd.Series

    Adapted from spmup by Cyril Pernet.

    S-outliers is the default options, it is independent of a measure of
    centrality as this is based on the median of pair-wise distances. This is
    a very sensitive measures, i.e. it has a relatively high false positive
    rates. As such it is a great detection tools.

    The adjusted Carling's box-plot rule can also be used, and derived from
    the median of the data: outliers are outside the bound of median +/- k*IQR,
    with k = (17.63*n-23.64)/(7.74*n-3.71). This is a more specific measure,
    as such it is 'better' than S-outliers to regress-out, removing bad data
    points (assuming we don't want to 'remove' too many).

    References:
        - :cite:t:`rousseeuw_alternatives_1993`
        - :cite:t:`carling_resistant_2000`
        - :cite:t:`hoaglin_performance_1986`


    """
    if outlier_type is None:
        outlier_type = "S-outliers"

    if outlier_type == "S-outliers":
        k = np.sqrt(chi2.ppf(0.975, df=1))

        non_nan_idx = time_series.index[~time_series.isnull()].tolist()

        distance = []
        for i in non_nan_idx:
            this_timepoint = time_series[i]

            # all but current data point
            indices = list(range(len(time_series)))
            indices.pop(i)

            tmp = time_series[indices]
            tmp.dropna(inplace=True)

            # median of all pair-wise distances
            distance.append(np.median(abs(this_timepoint - tmp)))

        # get the S estimator
        consistency_factor = 1.1926
        Sn = consistency_factor * np.median(distance)

        # get the outliers in a normal distribution
        # no scaling needed as S estimates already std(data)

        outliers = np.zeros(len(time_series), dtype=np.int8)
        outliers[non_nan_idx] = (distance / Sn) > k

        return outliers.tolist()

    elif outlier_type == "Carling":
        # interquartile range
        nan_less = time_series.dropna()
        nb_timepoints = len(nan_less)
        y = sorted(nan_less)
        j = math.floor(nb_timepoints / 4 + 5 / 12)
        g = (nb_timepoints / 4) - j + (5 / 12)
        k = nb_timepoints - j + 1

        lower_quartiles = (1 - g) * y[j] + g * y[j + 1]
        higher_quartiles = (1 - g) * y[k] + g * y[k - 1]
        inter_quartiles_range = higher_quartiles - lower_quartiles

        # robust outliers
        M = np.median(nan_less)
        carling_k = (17.63 * nb_timepoints - 23.64) / (7.74 * nb_timepoints - 3.71)
        lt = time_series < (M - carling_k * inter_quartiles_range)
        gt = time_series > (M + carling_k * inter_quartiles_range)
        df = pd.DataFrame({"lt": lt, "gt": gt})
        outliers = df["lt"] | df["gt"]

        return list(map(np.int8, outliers))  # type: ignore

    else:
        raise ValueError(f"Unknown outlier_type: {outlier_type}")
