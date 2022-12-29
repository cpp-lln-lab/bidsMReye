from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from bids import BIDSLayout  # type: ignore

from . import _version
from bidsmreye.configuration import Config
from bidsmreye.logging import bidsmreye_log

log = bidsmreye_log(name="bidsmreye")


__version__ = _version.get_versions()["version"]


def copy_license(output_dir: Path) -> Path:
    """Copy CCO license to output directory.

    :param output_dir:
    :type output_dir: Path
    """
    input_file = str(Path(__file__).parent.joinpath("templates", "CCO"))
    output_file = output_dir.joinpath("LICENSE")
    create_dir_if_absent(output_dir)
    if not output_dir.joinpath("LICENSE").is_file():
        shutil.copy(input_file, output_dir)
        move_file(output_dir.joinpath("CCO"), output_file)
    return output_file


def add_sidecar_in_root(layout_out: BIDSLayout) -> None:
    content = {
        "StartTime": 0,
        "SampleCoordinateUnit": "degrees",
        "EnvironmentCoordinates": "center",
        "SampleCoordinateSystem": "gaze-on-screen",
        "RecordedEye": "both",
    }
    sidecar_name = Path(layout_out.root).joinpath("desc-bidsmreye_eyetrack.json")
    json.dump(content, open(sidecar_name, "w"), indent=4)


def check_if_file_found(bf: Any, this_filter: dict[str, Any], layout: BIDSLayout) -> None:
    if len(bf) == 0:
        log.warning(f"No file found for filter {this_filter}")
    else:
        to_print = [str(Path(x).relative_to(layout.root)) for x in bf]
        log.debug(f"Found files\n{to_print}")


def set_this_filter(
    cfg: Config, subject_label: str | list[str], filter_type: str
) -> dict[str, Any]:

    this_filter = cfg.bids_filter[filter_type]
    this_filter["suffix"] = return_regex(this_filter["suffix"])
    this_filter["task"] = return_regex(cfg.task)
    if filter_type not in ("eyetrack", "eyetrack_qc"):
        this_filter["space"] = return_regex(cfg.space)
    this_filter["subject"] = subject_label
    if cfg.run:
        this_filter["run"] = return_regex(cfg.run)

    log.debug(f"Looking for files with filter\n{this_filter}")

    return this_filter


def move_file(input: Path, output: Path) -> None:
    """Move or rename a file and create target directory if it does not exist.

    Should work even the source and target names are on different file systems.

    :param input:File to move.
    :type input: Path

    :param output:
    :type output: Path

    :param root: Optional. If specified, the printed path will be relative to this path.
    :type root: Path
    """
    log.debug(f"{input.resolve()} --> {output.resolve()}")
    create_dir_for_file(output)
    shutil.copy(input, output)
    input.unlink()


def create_dir_if_absent(output_path: str | Path) -> None:
    """Create a path if it does not exist.

    :param output_path:
    :type output_path: Union[str, Path]
    """
    if isinstance(output_path, str):
        output_path = Path(output_path)
    if not output_path.is_dir():
        log.debug(f"Creating dir: {output_path}")
    output_path.mkdir(parents=True, exist_ok=True)


def create_dir_for_file(file: Path) -> None:
    """Create the path to a file if it does not exist.

    :param file:
    :type file: Path
    """
    output_path = file.resolve().parent
    create_dir_if_absent(output_path)

    # TODO refactor with create_dir_if_absent


def return_regex(value: str | list[str] | None) -> str | None:
    """Return the regular expression for a string or a list of strings.

    :param value:
    :type value: Union[str, Optional[list]]

    :return:
    :rtype: Optional[str]
    """
    if isinstance(value, str):
        if value[0] != "^":
            value = f"^{value}"
        if not value.endswith("$"):
            value = f"{value}$"

    if isinstance(value, list):
        new_value = ""
        for i in value:
            new_value = f"{new_value}{return_regex(i)}|"
        value = new_value[:-1]

    return value


def get_deepmreye_filename(
    layout: BIDSLayout, img: str, filetype: str | None = None
) -> Path:
    """Get deepmreye filename.

    :param layout: BIDSLayout of the dataset.
    :type layout: BIDSLayout

    :param img: _description_
    :type img: str

    :param filetype: Any of the following: None, "mask", "report"D defaults to None
    :type filetype: str, optional

    :raises ValueError: _description_

    :return: _description_
    :rtype: Path
    """
    if not img:
        raise ValueError("No file")

    if isinstance(img, (list)):
        img = img[0]

    bf = layout.get_file(img)
    filename = bf.filename

    filename = return_deepmreye_output_filename(filename, filetype)

    filefolder = Path(img).parent
    filefolder = filefolder.joinpath(filename)

    return Path(filefolder).resolve()


def return_deepmreye_output_filename(filename: str, filetype: str | None = None) -> str:
    """Return deepmreye output filename.

    :param filename:
    :type filename: str

    :param filetype: Any of the following: None, "mask", "report". defaults to None
    :type filetype: str, optional

    :return: _description_
    :rtype: str
    """
    if filetype is None:
        pass
    elif filetype == "mask":
        filename = "mask_" + re.sub(r"\.nii.*", ".p", filename)
    elif filetype == "report":
        filename = "report_" + re.sub(r"\.nii.*", ".html", filename)

    return filename
