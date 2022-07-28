"""TODO."""
import json
import logging
from pathlib import Path
from typing import Optional
from typing import Union

from bids import BIDSLayout  # type: ignore

from bidsmreye.utils import Config
from bidsmreye.utils import create_dir_if_absent

log = logging.getLogger("rich")


def get_dataset_layout(
    dataset_path: Union[str, Path],
    config: Optional[dict] = None,
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
    data = {
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
    }  # type: dict

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


def get_bidsname_config(config_file: Path = None) -> dict:
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


def get_pybids_config(config_file: Path = None) -> dict:
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


def get_bids_filter_config(config_file: Path = None) -> dict:
    """Load the bids filter file config.

    :param config_file: Config to load. Defaults to None.
    :type config_file: Path, optional

    :return: _description_
    :rtype: dict
    """
    default = "default_filter_file.json"
    return get_config(config_file, default)


def get_config(config_file: Path = None, default: str = "") -> dict:
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

    with open(config_file, "r") as ff:
        return json.load(ff)


def create_bidsname(
    layout: BIDSLayout, filename: Union[dict, str, Path], filetype: str
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
