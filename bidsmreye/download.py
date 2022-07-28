"""Download the models from OSF."""
import argparse
import logging
from pathlib import Path

import pkg_resources  # type: ignore
import pooch  # type: ignore
from rich.logging import RichHandler
from rich.traceback import install

from bidsmreye.utils import move_file

# let rich print the traceback
install(show_locals=True)

# log format
FORMAT = "bidsMReye - %(asctime)s - %(levelname)s - %(message)s"

logging.basicConfig(level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])
log = logging.getLogger("rich")


def main():
    """Download the models from OSF.

    :return: _description_
    :rtype: _type_
    """
    parser = argparse.ArgumentParser(description="bidsMReye model downloader.")
    parser.add_argument(
        "--model_name",
        help="""
        Model to download.
        """,
        choices=[
            "1_guided_fixations",
            "2_pursuit",
            "3_openclosed",
            "3_pursuit",
            "4_pursuit",
            "5_free_viewing",
            "all",
        ],
        default="1_guided_fixations",
    )
    parser.add_argument(
        "--output_dir",
        help="""
        The directory where the model files will be stored.
        """,
        default=Path.cwd().joinpath("models"),
    )

    args = parser.parse_args()

    download(model_name=args.model_name, output_dir=args.output_dir)


def download(model_name: str = None, output_dir: Path = None) -> Path:
    """Download the models from OSF.

    :param model_name: _description_, defaults to None
    :type model_name: str, optional

    :param output_dir: _description_, defaults to None
    :type output_dir: Path, optional

    :return: _description_
    :rtype: Path
    """
    if not model_name:
        model_name = "1_guided_fixations"

    if not output_dir:
        output_dir = Path.cwd().joinpath("models")

    OSF_ID = {
        "1_guided_fixations": "cqf74",
        "2_pursuit": "4f6m7",
        "3_openclosed": "8cr2j",
        "3_pursuit": "e89wp",
        "4_pursuit": "96nyp",
        "5_free_viewing": "89nky",
    }

    if model_name == "all":
        for key in list(OSF_ID):
            output_file = download(model_name=key, output_dir=output_dir)
        return output_file

    if model_name not in OSF_ID:
        raise ValueError(f"{model_name} is not a valid model name.")

    POOCH = pooch.create(
        path=output_dir,
        base_url="https://osf.io/download/",
        registry=None,
    )
    registry_file = pkg_resources.resource_stream("bidsmreye", "models/registry.txt")
    POOCH.load_registry(registry_file)

    output_file = output_dir.joinpath(f"dataset{model_name}.h5")

    if not output_file.is_file():

        fname = POOCH.fetch(OSF_ID[model_name], progressbar=True)
        move_file(Path(fname), output_file)

    else:
        log.info(f"{output_file} already exists.")

    return output_file
