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

from bidsmreye.utils import check_layout
from bidsmreye.utils import Config
from bidsmreye.utils import create_bidsname
from bidsmreye.utils import create_dir_for_file
from bidsmreye.utils import get_dataset_layout
from bidsmreye.utils import list_subjects
from bidsmreye.utils import set_this_filter
from bidsmreye.visualize import visualize_eye_gaze_data

log = logging.getLogger("bidsmreye")


def compute_displacement(x: pd.Series, y: pd.Series) -> pd.Series:

    return np.sqrt((x.diff() ** 2) + (y.diff() ** 2))


def add_qc_to_sidecar(layout: BIDSLayout, confounds_tsv: str | Path) -> Path:
    """_summary_

    :param layout: _description_
    :type layout: BIDSLayout

    :param confounds_tsv: _description_
    :type confounds_tsv: str | Path

    :return: _description_
    :rtype: Path
    """
    confounds_tsv = Path(confounds_tsv)
    confounds = pd.read_csv(confounds_tsv, sep="\t")

    sidecar_name = create_bidsname(layout, confounds_tsv, "confounds_json")

    with open(sidecar_name) as f:
        content = json.load(f)

        content["NbDisplacementOutliers"] = confounds["displacement_outliers"].sum()
        content["NbXOutliers"] = confounds["eye1_x_outliers"].sum()
        content["NbYOutliers"] = confounds["eye1_y_outliers"].sum()
        content["eye1XVar"] = confounds["eye1_x_coordinate"].var()
        content["eye1YVar"] = confounds["eye1_y_coordinate"].var()

    json.dump(content, open(sidecar_name, "w"), indent=4)

    return sidecar_name


def perform_quality_control(layout: BIDSLayout, confounds_tsv: str | Path) -> None:
    """Perform quality control on the confounds.

    :param layout: pybids layout to of the dataset to act on.
    :type layout: BIDSLayout

    :param confounds_tsv: Path to the confounds TSV file.
    :type confounds_tsv: str | Path
    """
    confounds_tsv = Path(confounds_tsv)
    confounds = pd.read_csv(confounds_tsv, sep="\t")

    repetition_time = get_repetition_time(layout, confounds_tsv)
    nb_timepoints = confounds.shape[0]
    eye_timestamp = np.arange(0, repetition_time * nb_timepoints, repetition_time)
    confounds["eye_timestamp"] = eye_timestamp

    cols = confounds.columns.tolist()
    cols.insert(0, cols.pop(cols.index("eye_timestamp")))
    confounds = confounds[cols]

    confounds["displacement"] = compute_displacement(
        confounds["eye1_x_coordinate"], confounds["eye1_y_coordinate"]
    )

    confounds["displacement_outliers"] = compute_robust_outliers(
        confounds["displacement"], outlier_type="Carling"
    )
    log.debug(f"Found {confounds['displacement_outliers'].sum()} displacement outliers")

    confounds["eye1_x_outliers"] = compute_robust_outliers(
        confounds["eye1_x_coordinate"], outlier_type="Carling"
    )
    log.debug(f"Found {confounds['eye1_x_outliers'].sum()} x outliers")

    confounds["eye1_y_outliers"] = compute_robust_outliers(
        confounds["eye1_y_coordinate"], outlier_type="Carling"
    )
    log.debug(f"Found {confounds['eye1_y_outliers'].sum()} y outliers")

    confounds.to_csv(confounds_tsv, sep="\t", index=False)

    sidecar_name = add_qc_to_sidecar(layout, confounds_tsv)
    log.info(f"Quality control data added to {sidecar_name}")

    fig = visualize_eye_gaze_data(confounds)
    if log.isEnabledFor(logging.DEBUG):
        fig.show()
    visualization_html_file = create_bidsname(layout, confounds_tsv, "confounds_html")
    create_dir_for_file(visualization_html_file)
    fig.write_html(visualization_html_file)


def get_repetition_time(layout: BIDSLayout, file: str | Path) -> float | None:
    """Get the repetition time from the sidecar JSON file."""
    repetition_time = None

    sidecar_name = create_bidsname(layout, file, "confounds_json")

    if sidecar_name.is_file():
        with open(sidecar_name) as f:
            content = json.load(f)
            SamplingFrequency = content.get("SamplingFrequency", None)
            if SamplingFrequency is not None and SamplingFrequency > 0:
                repetition_time = 1 / SamplingFrequency

    return repetition_time


def quality_control(cfg: Config) -> None:
    """Run quality control on the output dataset."""

    log.info("QUALITY CONTROL")

    layout_out = get_dataset_layout(cfg.output_folder)
    check_layout(cfg, layout_out)

    subjects = list_subjects(cfg, layout_out)

    for subject_label in subjects:

        qc_subject(cfg, layout_out, subject_label)


def qc_subject(cfg: Config, layout_out: BIDSLayout, subject_label: str) -> None:
    """Run quality control for one subject."""

    log.info(f"Running subject: {subject_label}")

    this_filter = set_this_filter(cfg, subject_label, "eyetrack")

    data = layout_out.get(
        return_type="filename",
        regex_search=True,
        **this_filter,
    )

    to_print = [str(Path(x).relative_to(layout_out.root)) for x in data]
    log.debug(f"Found files\n{to_print}")

    for file in data:

        perform_quality_control(layout_out, file)


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

    Adapted from spmup:
    https://github.com/CPernet/spmup/blob/master/QA/spmup_comp_robust_outliers.m

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

    - Rousseeuw, P. J., and Croux, C. (1993). Alternatives to the the median
    absolute deviation. J. Am. Stat. Assoc. 88, 1273-1263.
    <https://www.tandfonline.com/doi/abs/10.1080/01621459.1993.10476408>

    - Carling, K. (2000). Resistant outlier rules and the non-Gaussian case.
    Stat. Data Anal. 33, 249:258.
    <http://www.sciencedirect.com/science/article/pii/S0167947399000572>

    - Hoaglin, D.C., Iglewicz, B. (1987) Fine-tuning some resistant rules for
    outlier labelling. J. Amer. Statist. Assoc., 82 , 1147:1149
    <http://www.tandfonline.com/doi/abs/10.1080/01621459.1986.10478363>
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
