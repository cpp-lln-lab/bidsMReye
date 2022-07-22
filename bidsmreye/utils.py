"""foo."""
import os
import re
from os.path import abspath
from os.path import dirname
from os.path import join
from pathlib import Path
from typing import Optional

from bids import BIDSLayout  # type: ignore
from rich import print


def config() -> dict:
    """Return default configuration.

    Returns:
        dict: _description_
    """
    has_GPU = False

    os.environ["CUDA_VISIBLE_DEVICES"] = "0" if has_GPU else ""

    return {
        "output_folder": "",
        "input_folder": "",
        "model_weights_file": "",
        "participant": [],
        "space": "",
        "task": "",
        "debug": False,
    }


def move_file(input: str, output: str) -> None:
    """Move or rename a file and create target directory if it does not exist.

    Args:
        input (str): File to move.
        output (str): _description_
    """
    print(f"{abspath(input)} --> {abspath(output)}")
    create_dir_for_file(output)
    os.rename(input, output)


def create_dir_if_absent(output_path: str) -> None:
    """_summary_.

    Args:
        output_path (str): _description_
    """
    if not Path(output_path).exists():
        print(f"Creating dir: {output_path}")
        os.makedirs(output_path)


def create_dir_for_file(file: str) -> None:
    """_summary_.

    Args:
        file (str): _description_
    """
    output_path = dirname(abspath(file))
    create_dir_if_absent(output_path)


def return_regex(string: str) -> str:
    """_summary_.

    Args:
        string (_type_): _description_

    Returns:
        _type_: _description_
    """
    return f"^{string}$"


def list_subjects(layout, cfg: Optional[dict] = None) -> list:
    """_summary_.

    Args:
        layout (_type_): _description_
        cfg (dict or None, optional): _description_. Defaults to Nonz.

    Raises:
        Exception: _description_

    Returns:
        _type_: _description_
    """
    if cfg is None or cfg["participant"] == []:
        subjects = layout.get_subjects()
        debug = False
    else:
        subjects = layout.get(
            return_type="id", target="subject", subject=cfg["participant"]
        )
        debug = cfg["debug"]

    if subjects == [] or subjects is None:
        raise Exception("No subject found")

    if debug:
        subjects = [subjects[0]]

    print(f"processing subjects: {subjects}\n")

    return subjects


def return_path_rel_dataset(file_path: str, dataset_path: str) -> str:
    """Create file path relative to the root of a dataset."""
    file_path = abspath(file_path)
    dataset_path = abspath(dataset_path)
    rel_path = file_path.replace(dataset_path, "")
    rel_path = rel_path[1:]
    return rel_path


def get_deepmreye_filename(layout: BIDSLayout, img: str, filetype: str) -> str:
    """_summary_.

    Args:
        layout (_type_): _description_
        img (str): _description_
        filetype (str): _description_

    Raises:
        Exception: _description_

    Returns:
        str: _description_
    """
    if not img:
        raise Exception("No file")

    if isinstance(img, (list)):
        img = img[0]

    bf = layout.get_file(img)
    filename = bf.filename

    filename = return_deepmreye_output_filename(filename, filetype)

    filefolder = dirname(abspath(img))

    return join(filefolder, filename)


def return_deepmreye_output_filename(filename: str, filetype: str) -> str:
    """_summary_.

    Args:
        filename (str): _description_
        filetype (str): _description_

    Returns:
        str: _description_
    """
    if filetype == "mask":
        filename = "mask_" + re.sub(r"\.nii.*", ".p", filename)
    elif filetype == "report":
        filename = "report_" + re.sub(r"\.nii.*", ".html", filename)

    return filename
