from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from bidsmreye.download import download, download_parser


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


def test_download(tmp_path):
    download(model_name="1_guided_fixations", output_dir=str(tmp_path))

    assert tmp_path.is_dir()
    assert (tmp_path / "dataset_1_guided_fixations.h5").is_file()


def test_download_basic():
    download()
    output_file = download()

    output_dir = Path.cwd().joinpath("models")
    print(output_file)
    assert output_dir.is_dir()
    assert output_dir.joinpath("dataset_1to6.h5").is_file()

    shutil.rmtree(output_dir)


def test_download_unknown_model():
    with pytest.warns(UserWarning):
        download(model_name="foo")
