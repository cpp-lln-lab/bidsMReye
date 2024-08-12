from __future__ import annotations

from bidsmreye._parsers import common_parser, download_parser


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
            "--linear_coreg",
        ]
    )

    assert args.task == ["foo", "bar"]
    assert args.linear_coreg


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
    assert args.linear_coreg is False


def test_download_parser():
    parser = download_parser()

    assert parser.description == "Download deepmreye pretrained model from OSF."

    args, _ = parser.parse_known_args(
        [
            "--model",
            "1_guided_fixations",
            "--output_dir",
            "/home/bob/models",
        ]
    )

    assert args.output_dir == "/home/bob/models"
