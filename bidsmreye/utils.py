"""TODO."""
import logging
import os
import re
import warnings
from pathlib import Path
from typing import Optional

from attrs import define
from attrs import field
from bids import BIDSLayout  # type: ignore

log = logging.getLogger("rich")


@define
class Config:
    """Set up config and check that all required fields are set."""

    input_folder: str = field(default=None, converter=Path)

    @input_folder.validator
    def _check_input_folder(self, attribute, value):
        if not value.is_dir:
            raise ValueError(f"Input_folder must be an existing directory:\n{value}.")

    output_folder: str = field(default=None, converter=Path)
    model_weights_file = field(kw_only=True, default="")
    participant: list = field(kw_only=True, default=[])
    space: str = field(kw_only=True, default="")
    task: str = field(kw_only=True, default="")
    debug: bool = field(kw_only=True, default=False)
    has_GPU = False

    def __attrs_post_init__(self):
        """Check that output_folder exists and gets info from layout if not specified."""
        os.environ["CUDA_VISIBLE_DEVICES"] = "0" if self.has_GPU else ""

        self.output_folder = Path(self.output_folder).joinpath("bidsmreye")
        if not self.output_folder:
            self.output_folder.mkdir(parents=True, exist_ok=True)

        layout_in = BIDSLayout(self.input_folder, validate=False, derivatives=False)

        # TODO throw error if no participants found or warning
        #      if some requested participants are not found
        subjects = layout_in.get_subjects()
        if self.participant:
            missing_subjects = list(set(self.participant) - set(subjects))
            if missing_subjects:
                warnings.warn(
                    f"Task(s) {missing_subjects} not found in {self.input_folder}"
                )
            self.participant = list(set(self.participant) & set(subjects))
        else:
            self.participant = layout_in.get(
                return_type="id", target="subject", subject=self.participant
            )

        # TODO throw error if no task found or warning
        #      if some requested tasks are not found
        tasks = layout_in.get_tasks()
        if not self.task:
            self.task = layout_in.get_tasks()
        else:
            missing_tasks = list(set(self.task) - set(tasks))
            if missing_tasks:
                warnings.warn(f"Task(s) {missing_tasks} not found in {self.input_folder}")
            self.task = list(set(self.task) & set(tasks))


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


def move_file(input: Path, output: Path) -> None:
    """Move or rename a file and create target directory if it does not exist.

    Args:
        input (Path): File to move.

        output (str): _description_
    """
    log.info(f"{input.resolve()} --> {output.resolve()}")
    create_dir_for_file(output)
    input.rename(output)


def create_dir_if_absent(output_path: Path) -> None:
    """_summary_.

    Args:
        output_path (Path): _description_
    """
    if not output_path.is_dir():
        log.info(f"Creating dir: {output_path}")
    output_path.mkdir(parents=True, exist_ok=True)


def create_dir_for_file(file: Path) -> None:
    """_summary_.

    Args:
        file (Path): _description_
    """
    output_path = file.resolve().parent
    create_dir_if_absent(output_path)


def return_regex(string: str) -> str:
    """_summary_.

    Args:
        string (_type_): _description_

    Returns:
        _type_: _description_
    """
    return f"^{string}$"


def list_subjects(layout: BIDSLayout, cfg: Optional[dict] = None) -> list:
    """_summary_.

    Args:
        layout (BIDSLayout): BIDSLayout of the dataset

        cfg (dict or None, optional): Defaults to None.

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
        log.debug("Running first subject only.")

    log.info(f"processing subjects: {subjects}")

    return subjects


def get_deepmreye_filename(layout: BIDSLayout, img: str, filetype: str = None) -> Path:
    """_summary_.

    Args:
        layout (BIDSLayout): BIDSLayout of the dataset.

        img (str): _description_

        filetype (str): Any of the following: None, "mask", "report". Defautls to None.

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

    filefolder = Path(img).parent
    filefolder = filefolder.joinpath(filename)

    return Path(filefolder).resolve()


def return_deepmreye_output_filename(filename: str, filetype: str = None) -> str:
    """_summary_.

    Args:
        filename (str): _description_

        filetype (str): Any of the following: None, "mask", "report". Defautls to None.

    Returns:
        str: _description_
    """
    if filetype is None:
        pass
    elif filetype == "mask":
        filename = "mask_" + re.sub(r"\.nii.*", ".p", filename)
    elif filetype == "report":
        filename = "report_" + re.sub(r"\.nii.*", ".html", filename)

    return filename
