"""TODO."""
from __future__ import annotations

import json
import logging
import math
from pathlib import Path

import numpy as np
import pandas as pd
from bids import BIDSLayout  # type: ignore
from scipy.stats.distributions import chi2

from bidsmreye.bids_utils import check_layout
from bidsmreye.bids_utils import create_bidsname
from bidsmreye.bids_utils import get_dataset_layout
from bidsmreye.bids_utils import init_dataset
from bidsmreye.bids_utils import list_subjects
from bidsmreye.configuration import Config
from bidsmreye.logging import bidsmreye_log
from bidsmreye.utils import check_if_file_found
from bidsmreye.utils import create_dir_for_file
from bidsmreye.utils import set_this_filter
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

    content["NbDisplacementOutliers"] = confounds["displacement_outliers"].sum()
    content["NbXOutliers"] = confounds["eye1_x_outliers"].sum()
    content["NbYOutliers"] = confounds["eye1_y_outliers"].sum()
    content["eye1XVar"] = confounds["eye1_x_coordinate"].var()
    content["eye1YVar"] = confounds["eye1_y_coordinate"].var()

    json.dump(content, open(sidecar_name, "w"), indent=4)


def compute_displacement_and_outliers(confounds: pd.DataFrame) -> pd.DataFrame:

    confounds["displacement"] = compute_displacement(
        confounds["eye1_x_coordinate"], confounds["eye1_y_coordinate"]
    )

    confounds["displacement_outliers"] = compute_robust_outliers(
        confounds["displacement"], outlier_type="Carling"
    )

    confounds["eye1_x_outliers"] = compute_robust_outliers(
        confounds["eye1_x_coordinate"], outlier_type="Carling"
    )
    log.debug(f"Found {confounds['eye1_x_outliers'].sum()} x outliers")

    confounds["eye1_y_outliers"] = compute_robust_outliers(
        confounds["eye1_y_coordinate"], outlier_type="Carling"
    )
    log.debug(f"Found {confounds['eye1_y_outliers'].sum()} y outliers")

    return confounds


def perform_quality_control(
    layout_in: BIDSLayout, confounds_tsv: str | Path, layout_out: BIDSLayout | None = None
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
    confounds = pd.read_csv(confounds_tsv, sep="\t")

    if "eye_timestamp" not in confounds.columns:

        sampling_frequency = get_sampling_frequency(layout_in, confounds_tsv)

        if sampling_frequency is not None:
            nb_timepoints = confounds.shape[0]
            eye_timestamp = np.arange(
                0, 1 / sampling_frequency * nb_timepoints, 1 / sampling_frequency
            )
            confounds["eye_timestamp"] = eye_timestamp

            cols = confounds.columns.tolist()
            cols.insert(0, cols.pop(cols.index("eye_timestamp")))
            confounds = confounds[cols]

    compute_displacement_and_outliers(confounds)

    sidecar_name = create_bidsname(layout_out, confounds_tsv, "confounds_json")
    add_qc_to_sidecar(confounds, sidecar_name)

    fig = visualize_eye_gaze_data(confounds)
    fig.update_layout(title=Path(confounds_tsv).name)
    if log.isEnabledFor(logging.DEBUG):
        fig.show()
    visualization_html_file = create_bidsname(layout_out, confounds_tsv, "confounds_html")
    create_dir_for_file(visualization_html_file)
    fig.write_html(visualization_html_file)

    confounds_tsv = create_bidsname(layout_out, confounds_tsv, "confounds_tsv")
    confounds.to_csv(confounds_tsv, sep="\t", index=False)


def get_sampling_frequency(layout: BIDSLayout, file: str | Path) -> float | None:
    """Get the sampling frequency from the sidecar JSON file."""
    sampling_frequency = None

    sidecar_name = create_bidsname(layout, file, "confounds_json")

    # TODO: deal with cases where the sidecar is in the root of the dataset
    if sidecar_name.is_file():
        with open(sidecar_name) as f:
            content = json.load(f)
            SamplingFrequency = content.get("SamplingFrequency", None)
            if SamplingFrequency is not None and SamplingFrequency > 0:
                sampling_frequency = SamplingFrequency

    return sampling_frequency


def quality_control_output(cfg: Config) -> None:
    """Run quality control on the output dataset."""

    log.info("QUALITY CONTROL")

    layout_out = get_dataset_layout(cfg.output_dir)
    check_layout(cfg, layout_out)

    subjects = list_subjects(cfg, layout_out)

    for subject_label in subjects:

        qc_subject(cfg, layout_out, subject_label)


def quality_control_input(cfg: Config) -> None:
    """Run quality control on the input dataset."""

    log.info("QUALITY CONTROL")

    layout_in = get_dataset_layout(cfg.input_dir)
    check_layout(cfg, layout_in, "eyetrack")

    layout_out = init_dataset(cfg, qc_only=True)

    subjects = list_subjects(cfg, layout_in)

    for subject_label in subjects:

        qc_subject(cfg, layout_in, subject_label, layout_out)


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
        return_type="filename",
        regex_search=True,
        **this_filter,
    )

    check_if_file_found(bf, this_filter, layout_in)

    for file in bf:

        perform_quality_control(layout_in, file, layout_out)


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

    Adapted from
    `spmup <https://github.com/CPernet/spmup/blob/master/QA/spmup_comp_robust_outliers.m>`_


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

    - `Rousseeuw, P. J., and Croux, C. (1993). Alternatives to the the median
      absolute deviation. J. Am. Stat. Assoc. 88, 1273-1263.
      <https://www.tandfonline.com/doi/abs/10.1080/01621459.1993.10476408>`_

    - `Carling, K. (2000). Resistant outlier rules and the non-Gaussian case.
      Stat. Data Anal. 33, 249:258.
      <http://www.sciencedirect.com/science/article/pii/S0167947399000572>`_

    - `Hoaglin, D.C., Iglewicz, B. (1987) Fine-tuning some resistant rules for
      outlier labelling. J. Amer. Statist. Assoc., 82 , 1147:1149
      <http://www.tandfonline.com/doi/abs/10.1080/01621459.1986.10478363>`_
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

        outliers = np.zeros(len(time_series))
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

        return list(map(float, outliers))  # type: ignore

    else:
        raise ValueError(f"Unknown outlier_type: {outlier_type}")
