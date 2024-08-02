from __future__ import annotations

from bidsmreye.bidsmreye import common_parser
from bidsmreye.download import download_parser


def test_parser() -> None:
    parser = common_parser()
    args, _ = parser.parse_known_args(
        [
            "/path/to/bids",
            "/path/to/output",
            "participant",
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

    args, _ = parser.parse_known_args(
        [
            "/path/to/bids",
            "/path/to/output",
            "participant",
            "prepare",
            "--task",
            "foo",
            "bar",
        ]
    )

    assert args.task == ["foo", "bar"]
    assert args.non_linear_coreg == False


def test_download_parser():
    parser = download_parser()

    assert parser.description == "Download deepmreye pretrained model from OSF."

    args, _ = parser.parse_known_args(
        [
            "--model_name",
            "1_guided_fixations",
            "--output_dir",
            "/home/bob/models",
        ]
    )

    assert args.output_dir == "/home/bob/models"
