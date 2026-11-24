from pathlib import Path

import pytest

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


@pytest.fixture
def model_file(tmp_path) -> Path:
    """Fake model weights file."""
    model_file = tmp_path / "my_model.h5"
    model_file.write_bytes(b"")
    return model_file


@pytest.mark.parametrize("action", ["generalize", "all"])
def test_parser_model_name(action) -> None:
    args = common_parser().parse_args(
        ["/path/to/bids", "/path/to/output", "participant", action, "--model", "1to5"]
    )

    assert args.model == "1to5"


@pytest.mark.parametrize("action", ["generalize", "all"])
def test_parser_model_path(action, model_file) -> None:
    """Can pass the path to a model weights file.

    https://github.com/cpp-lln-lab/bidsMReye/issues/91
    """
    args = common_parser().parse_args(
        [
            "/path/to/bids",
            "/path/to/output",
            "participant",
            action,
            "--model",
            str(model_file),
        ]
    )

    assert Path(args.model) == model_file


@pytest.mark.parametrize("action", ["generalize", "all"])
@pytest.mark.parametrize("model", ["foo", "/no/such/model.h5"])
def test_parser_model_invalid(action, model, capsys) -> None:
    """Reject models that are neither a known model nor an existing file."""
    with pytest.raises(SystemExit):
        common_parser().parse_args(
            ["/path/to/bids", "/path/to/output", "participant", action, "--model", model]
        )

    assert model in capsys.readouterr().err
