"""TODO."""
from __future__ import annotations

import json
import logging
import os
import re
import shutil
import warnings
from pathlib import Path
from typing import Any

from attrs import converters
from attrs import define
from attrs import field
from bids import BIDSLayout
from rich.logging import RichHandler
from rich.traceback import install

log = logging.getLogger("bidsmreye")


def bidsmreye_log(name: str | None = None) -> logging.Logger:
    """Create log.

    :param name: _description_, defaults to None
    :type name: _type_, optional

    :return: _description_
    :rtype: _type_
    """
    # let rich print the traceback
    install(show_locals=True)

    FORMAT = "bidsMReye - %(asctime)s - %(levelname)s - %(message)s"

    log_level = "INFO"

    if not name:
        name = "rich"

    logging.basicConfig(
        level=log_level, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

    return logging.getLogger(name)


@define
class Config:
    """Set up config and check that all required fields are set.

    :raises ValueError: _description_
    :raises RuntimeError: _description_

    :return: _description_
    :rtype: _type_
    """

    input_folder = field(default=None, converter=Path)

    @input_folder.validator
    def _check_input_folder(self, attribute: str, value: Path) -> None:
        if not value.is_dir:  # type: ignore
            raise ValueError(f"Input_folder must be an existing directory:\n{value}.")

    output_folder: Path = field(default=None, converter=Path)
    participant: Any | None = field(kw_only=True, default=None)
    space: Any | None = field(kw_only=True, default=None)
    task: Any | None = field(kw_only=True, default=None)
    run: Any | None = field(kw_only=True, default=None)
    model_weights_file: str | Path | None = field(kw_only=True, default=None)
    debug: str | bool | None = field(kw_only=True, default=None)
    reset_database: str | bool | None = field(kw_only=True, default=None)
    bids_filter: Any = field(kw_only=True, default=None)
    has_GPU = False

    def __attrs_post_init__(self) -> None:
        """Check that output_folder exists and gets info from layout if not specified."""
        os.environ["CUDA_VISIBLE_DEVICES"] = "0" if self.has_GPU else ""

        if not self.debug:
            self.debug = False
        if not isinstance(self.debug, (bool)):
            self.debug = converters.to_bool(self.debug)

        if not self.reset_database:
            self.reset_database = False
        if not isinstance(self.reset_database, (bool)):
            self.reset_database = converters.to_bool(self.reset_database)

        if not self.run:
            self.run = []

        # TODO test for passing bids_filter
        if not self.bids_filter:
            self.bids_filter = get_bids_filter_config()

        self.output_folder = self.output_folder.joinpath("bidsmreye")
        if not self.output_folder:
            self.output_folder.mkdir(parents=True, exist_ok=True)

        database_path = self.input_folder.joinpath("pybids_db")

        layout_in = BIDSLayout(
            self.input_folder,
            validate=False,
            derivatives=False,
            database_path=database_path,
            reset_database=self.reset_database,
        )

        if not database_path.is_dir():
            layout_in.save(database_path)

        self.check_argument(attribute="participant", layout_in=layout_in)
        self.check_argument(attribute="task", layout_in=layout_in)
        self.check_argument(attribute="run", layout_in=layout_in)
        self.check_argument(attribute="space", layout_in=layout_in)

    def check_argument(self, attribute: str, layout_in: BIDSLayout) -> Config:
        """Check an attribute value compared to a the input dataset content.

        :param attribute:
        :type attribute: _type_

        :param layout_in:
        :type layout_in: BIDSLayout

        :raises RuntimeError:

        :return:
        :rtype: _type_
        """
        if attribute == "participant":
            value = layout_in.get_subjects()
        elif attribute == "task":
            value = layout_in.get_tasks()
        elif attribute in {"space", "run"}:
            value = layout_in.get(return_type="id", target=attribute, datatype="func")

        self.listify(attribute)

        # convert all run values to integers
        if attribute in {"run"}:
            for i, j in enumerate(value):
                value[i] = int(j)
            tmp = [int(j) for j in getattr(self, attribute)]
            setattr(self, attribute, tmp)

        # keep only values that are intersection of requested values
        # and those present in the dataset
        if getattr(self, attribute):
            if missing_values := list(set(getattr(self, attribute)) - set(value)):
                warnings.warn(
                    f"{attribute}(s) {missing_values} not found in {self.input_folder}"
                )
            value = list(set(getattr(self, attribute)) & set(value))

        setattr(self, attribute, value)

        # run can be empty if run entity is not used
        if attribute not in ["run"] and not getattr(self, attribute):
            raise RuntimeError(f"No {attribute} not found in {self.input_folder}")

        return self

    def listify(self, attribute: str) -> Config:
        """Convert attribute to list if not already."""
        if getattr(self, attribute) and not isinstance(getattr(self, attribute), list):
            setattr(self, attribute, [getattr(self, attribute)])

        return self


def move_file(input: Path, output: Path) -> None:
    """Move or rename a file and create target directory if it does not exist.

    Should work even the source and target names are on different file systems.

    :param input:File to move.
    :type input: Path

    :param output:
    :type output: Path
    """
    log.info(f"{input.resolve()} --> {output.resolve()}")
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
        log.info(f"Creating dir: {output_path}")
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


def list_subjects(cfg: Config, layout: BIDSLayout) -> list[str]:
    """List subject in a BIDS dataset for a given Config.

    :param cfg: Configuration object
    :type cfg: Config

    :param layout: BIDSLayout of the dataset.
    :type layout: BIDSLayout

    :raises RuntimeError: _description_

    :return: _description_
    :rtype: list
    """
    subjects = layout.get(return_type="id", target="subject", subject=cfg.participant)

    if subjects == [] or subjects is None:
        raise RuntimeError("No subject found")

    if cfg.debug:
        subjects = [subjects[0]]
        log.debug("Running first subject only.")

    log.info(f"processing subjects: {subjects}")

    return subjects


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


def get_dataset_layout(
    dataset_path: str | Path,
    config: dict[str, str] | None = None,
    use_database: bool = False,
) -> BIDSLayout:
    """Return a BIDSLayout object for the dataset at the given path.

    :param dataset_path: Path to the dataset.
    :type dataset_path: Union[str, Path]

    :param config: Pybids config to use. Defaults to None.
    :type config: Optional[dict], optional

    :param use_database: Defaults to False
    :type use_database: bool, optional

    :return: _description_
    :rtype: BIDSLayout
    """
    if isinstance(dataset_path, str):
        dataset_path = Path(dataset_path)
    create_dir_if_absent(dataset_path)

    if config is None:
        pybids_config = get_pybids_config()

    log.info(f"indexing {dataset_path}")

    if not use_database:
        return BIDSLayout(
            dataset_path,
            validate=False,
            derivatives=False,
            config=pybids_config,
        )

    database_path = dataset_path.joinpath("pybids_db")
    return BIDSLayout(
        dataset_path,
        validate=False,
        derivatives=False,
        config=pybids_config,
        database_path=database_path,
    )


def write_dataset_description(layout: BIDSLayout) -> None:
    """Add a dataset_description.json to a BIDS dataset.

    :param layout: BIDSLayout of the dataset to update.
    :type layout: BIDSLayout
    """
    output_file = Path(layout.root).joinpath("dataset_description.json")

    with open(output_file, "w") as ff:
        json.dump(layout.dataset_description, ff, indent=4)


def set_dataset_description(layout: BIDSLayout, is_derivative: bool = True) -> BIDSLayout:
    """Add dataset description to a layout.

    :param layout: _description_
    :type layout: BIDSLayout

    :param is_derivative: Defaults to True
    :type is_derivative: bool, optional

    :return: Updated BIDSLayout of the dataset
    :rtype: BIDSLayout
    """
    data: dict[str, Any] = {
        "Name": "dataset name",
        "BIDSVersion": "1.6.0",
        "DatasetType": "raw",
        "License": "",
        "Authors": ["", ""],
        "Acknowledgements": "Special thanks to ",
        "HowToAcknowledge": "Please cite this paper: ",
        "Funding": ["", ""],
        "EthicsApprovals": [""],
        "ReferencesAndLinks": ["", ""],
        "DatasetDOI": "doi:",
        "HEDVersion": "",
    }

    if is_derivative:
        data["GeneratedBy"] = [
            {
                "Name": "",
                "Version": "",
                "Container": {"Type": "", "Tag": ""},
                "Description": "",
                "CodeURL": "",
            },
        ]

        data["SourceDatasets"] = [
            {
                "DOI": "doi:",
                "URL": "",
                "Version": "",
            }
        ]

    layout.dataset_description = data

    return layout


def init_derivatives_layout(output_location: Path) -> BIDSLayout:
    """Initialize a derivatives dataset and returns its layout.

    :param output_location:
    :type output_location: Path

    :return:
    :rtype: BIDSLayout
    """
    layout_out = get_dataset_layout(output_location)
    layout_out = set_dataset_description(layout_out)
    layout_out.dataset_description["DatasetType"] = "derivative"
    layout_out.dataset_description["GeneratedBy"][0]["Name"] = "bidsmreye"
    write_dataset_description(layout_out)
    return layout_out


def get_bidsname_config(config_file: Path | None = None) -> dict[str, str]:
    """Load configuration for naming output BIDS files.

    :param config_file: Defaults to None
    :type config_file: Path, optional

    :return: Config as a dictionary.
    :rtype: dict

    See the Path construction demo in the pybids tutorial.

    https://github.com/bids-standard/pybids/blob/master/examples/pybids_tutorial.ipynb
    """
    default = "config_bidsname.json"
    return get_config(config_file, default)


def get_pybids_config(config_file: Path | None = None) -> dict[str, str]:
    """Load pybids configuration.

    :param config_file: Defaults to None
    :type config_file: Path, optional
    :return: _description_
    :rtype: dict

    Pybids configs are stored in the layout module.

    https://github.com/bids-standard/pybids/tree/master/bids/layout/config
    """
    default = "config_pybids.json"
    return get_config(config_file, default)


def get_bids_filter_config(config_file: Path | None = None) -> dict[str, Any]:
    """Load the bids filter file config.

    :param config_file: Config to load. Defaults to None.
    :type config_file: Path, optional

    :return: _description_
    :rtype: dict
    """
    default = "default_filter_file.json"
    return get_config(config_file, default)


def get_config(config_file: Path | None = None, default: str = "") -> dict[str, str]:
    """Load a config stored in a JSON.

    :param config_file: File to load. Defaults to None.
                        Will look into the config directory if None.
    :type config_file: Path, optional

    :param default: Default file to load. Defaults to ""
    :type default: str, optional

    :raises FileNotFoundError: _description_

    :return: Config as a dictionary.
    :rtype: dict
    """
    if config_file is None or not Path(config_file).exists():
        my_path = Path(__file__).resolve().parent.joinpath("config")
        config_file = my_path.joinpath(default)

    if config_file is None or not Path(config_file).exists():
        raise FileNotFoundError(f"Config file {config_file} not found")

    with open(config_file) as ff:
        return json.load(ff)


def create_bidsname(
    layout: BIDSLayout, filename: dict[str, str] | str | Path, filetype: str
) -> Path:
    """Return a BIDS valid filename for layout and a filename or a dict of BIDS entities.

    :param layout: BIDSLayout of the dataset.
    :type layout: BIDSLayout

    :param filename: Dictionary of BIDS entities or a Path to a file.
    :type filename: Union[dict, str, Path]

    :param filetype: One of the file type available in the BIDS name config.
    :type filetype: str

    :raises TypeError:

    :return:
    :rtype: Path
    """
    if isinstance(filename, dict):
        entities = filename
    elif isinstance(filename, (Path, str)):
        entities = layout.parse_file_entities(filename)
    else:
        raise TypeError(f"filename must be a dict or a Path, not {type(filename)}")

    bids_name_config = get_bidsname_config()

    output_file = layout.build_path(entities, bids_name_config[filetype], validate=False)

    output_file = Path(layout.root).joinpath(output_file)

    return output_file.resolve()


def check_layout(cfg: Config, layout: BIDSLayout) -> None:
    """Check layout.

    :param cfg: Configuration object
    :type cfg: Config

    :param layout: BIDSLayout of the dataset.
    :type layout: BIDSLayout

    :raises RuntimeError: _description_
    :raises RuntimeError: _description_
    """
    desc = layout.get_dataset_description()
    if (
        "DatasetType" not in desc
        and "PipelineDescription" not in desc
        or "DatasetType" in desc
        and desc["DatasetType"] != "derivative"
    ):
        raise RuntimeError("Input dataset should be BIDS derivative")

    this_filter = get_bids_filter_config()["bold"]

    if "GeneratedBy" in desc:
        generated_by = desc["GeneratedBy"]
    elif "PipelineDescription" in desc:
        generated_by = desc["PipelineDescription"]

    if isinstance(generated_by, list):
        generated_by = generated_by[0]

    if generated_by["Name"].lower() == "bidsmreye":
        this_filter = get_bids_filter_config()["mask"]

    this_filter["task"] = cfg.task
    this_filter["space"] = cfg.space
    this_filter["run"] = cfg.run

    log.debug(f"Looking for files with filter\n{this_filter}")

    bf = layout.get(
        return_type="filename",
        regex_search=True,
        **this_filter,
    )

    if bf == []:
        raise RuntimeError(
            f"""
            Input dataset {layout.root} does not have any data to process for filter\n{this_filter}
            """
        )
