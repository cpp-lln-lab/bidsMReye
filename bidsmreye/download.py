"""Download the models from OSF."""
from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path
from typing import Any
from typing import IO

import pkg_resources
import pooch
import rich

from bidsmreye.defaults import available_models
from bidsmreye.defaults import default_model
from bidsmreye.logging import bidsmreye_log

log = bidsmreye_log(name="bidsmreye")


class MuhParser(argparse.ArgumentParser):
    """Parser for the main script."""

    def _print_message(self, message: str, file: IO[str] | None = None) -> None:
        rich.print(message, file=file)


def download_parser() -> MuhParser:
    """Execute the main script."""
    parser = MuhParser(
        description="Download deepmreye pretrained model from OSF.",
        epilog="""
        For a more readable version of this help section,
        see the online https://bidsmreye.readthedocs.io/.
        """,
    )
    parser.add_argument(
        "--model_name",
        help="""
        Model to download.
        """,
        choices=available_models(),
        default=default_model(),
    )
    parser.add_argument(
        "--output_dir",
        help="""
        The directory where the model files will be stored.
        """,
        default=Path.cwd().joinpath("models"),
    )

    return parser


def cli(argv: Any = sys.argv) -> None:
    """Download the models from OSF.

    :return: _description_
    :rtype: _type_
    """
    parser = download_parser()
    args = parser.parse_args(argv[1:])

    download(model_name=args.model_name, output_dir=args.output_dir)


def download(
    model_name: str | Path | None = None, output_dir: Path | str | None = None
) -> Path | None:
    """Download the models from OSF.

    :param model_name: Model to download. defaults to None
    :type model_name: str, optional

    :param output_dir: Path where to save the model. Defaults to None.
    :type output_dir: Path, optional

    :return: Path to the downloaded model.
    :rtype: Path
    """
    if not model_name:
        model_name = default_model()
    if isinstance(model_name, Path):
        assert model_name.is_file()
        return model_name.resolve()
    if model_name not in available_models():
        warnings.warn(f"{model_name} is not a valid model name.")
        return None

    if output_dir is None:
        output_dir = Path.cwd().joinpath("models")
    if isinstance(output_dir, str):
        output_dir = Path(output_dir)

    POOCH = pooch.create(
        path=output_dir,
        base_url="https://osf.io/download/",
        registry=None,
    )
    registry_file = pkg_resources.resource_stream("bidsmreye", "models/registry.txt")
    POOCH.load_registry(registry_file)

    output_file = output_dir.joinpath(f"dataset_{model_name}")

    if not output_file.is_file():

        file_idx = available_models().index(model_name)
        filename = f"dataset_{available_models()[file_idx]}.h5"
        output_file = POOCH.fetch(filename, progressbar=True)
        if isinstance(output_file, str):
            output_file = Path(output_file)

    else:
        log.info(f"{output_file} already exists.")

    return output_file
