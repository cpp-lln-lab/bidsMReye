from __future__ import annotations

import numpy as np
import pandas as pd

from bidsmreye.quality_control import compute_robust_outliers


def time_series():

    return [
        0.6876,
        0.9751,
        0.1322,
        0.2420,
        1.4233,
        1.2617,
        -0.8619,
        -0.9471,
        2.6217,
        -0.6192,
        -1.0646,
        -0.4872,
        -0.1146,
        0.3007,
        -0.4089,
        0.1137,
        -0.0946,
        0.7829,
        1.8999,
        -1.0088,
    ]


def test_compute_robust_outliers():

    outliers = compute_robust_outliers(pd.Series(time_series()))

    expected_outliers = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    assert outliers == expected_outliers


def test_compute_robust_with_nan():

    series = time_series()
    series[1] = np.nan
    series[8] = 10

    outliers = compute_robust_outliers(pd.Series(series))

    expected_outliers = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    assert outliers == expected_outliers
