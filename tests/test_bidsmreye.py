from __future__ import annotations

from bidsmreye.bidsmreye import bidsmreye
from bidsmreye.bidsmreye import common_parser


def test_parser() -> None:
    parser = common_parser()
    args, unknowns = parser.parse_known_args(
        [
            "/path/to/bids",
            "/path/to/output",
            "participant",
            "--action",
            "prepare",
            "--task",
            "foo",
            "bar",
            "--non_linear_coreg",
        ]
    )

    assert args.task == ["foo", "bar"]
    assert args.non_linear_coreg


def test_parser_basic() -> None:

    parser = common_parser()

    assert (
        parser.description
        == "BIDS app using deepMReye to decode eye motion for fMRI time series data."
    )

    args, unknowns = parser.parse_known_args(
        [
            "/path/to/bids",
            "/path/to/output",
            "participant",
            "--action",
            "prepare",
            "--task",
            "foo",
            "bar",
        ]
    )

    assert args.task == ["foo", "bar"]
    assert args.non_linear_coreg == False
