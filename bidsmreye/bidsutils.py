"""TODO."""
import json
from pathlib import Path
from typing import Optional
from typing import Union

from bids import BIDSLayout  # type: ignore
from rich import print

from bidsmreye.utils import config
from bidsmreye.utils import create_dir_if_absent


def get_dataset_layout(dataset_path: Path, config: Optional[dict] = None) -> BIDSLayout:
    """Return a BIDSLayout object for the dataset at the given path.

    Args:
        dataset_path (Path): Path to the dataset.

        config (dict, None): Pybids config to use. Defaults to None.

    Returns:
        BIDSLayout: _description_
    """
    create_dir_if_absent(dataset_path)

    if config is None:
        pybids_config = get_pybids_config()

    print(f"\nindexing {dataset_path}\n")

    return BIDSLayout(
        dataset_path, validate=False, derivatives=False, config=pybids_config
    )


def write_dataset_description(layout: BIDSLayout) -> None:
    """Add a dataset_description.json to a BIDS dataset.

    Args:
        layout (BIDSLayout): BIDSLayout of the dataset to update.
    """
    output_file = Path(layout.root).joinpath("dataset_description.json")

    with open(output_file, "w") as ff:
        json.dump(layout.dataset_description, ff, indent=4)


def set_dataset_description(layout: BIDSLayout, is_derivative: bool = True) -> BIDSLayout:
    """Add dataset description to a layout.

    Args:
        layout (BIDSLayout): _description_

        is_derivative (bool, optional): Defaults to True.

    Returns:
        BIDSLayout: Updated BIDSLayout of the dataset
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

    Args:
        output_location (_type_): _description_

    Returns:
        BIDSLayout:
    """
    layout_out = get_dataset_layout(output_location)
    layout_out = set_dataset_description(layout_out)
    layout_out.dataset_description["DatasetType"] = "derivative"
    layout_out.dataset_description["GeneratedBy"][0]["Name"] = "bidsmreye"
    write_dataset_description(layout_out)
    return layout_out


def get_bidsname_config(config_file: Path = None) -> dict:
    """Load configuration for naming output BIDS files.

    Args:
        config_file (Path, optional): Defaults to None.

    Returns:
        dict: Config as a dictionary.

    See the Path construction demo in the pybids tutorial.

    https://github.com/bids-standard/pybids/blob/master/examples/pybids_tutorial.ipynb
    """
    default = "config_bidsname.json"
    return get_config(config_file, default)


def get_pybids_config(config_file: Path = None) -> dict:
    """Load pybids coniguration.

    Args:
        config_file (Path, optional): Defaults to None.

    Returns:
        dict: pybids config.

    Pybids configs are stored in the layout module.

    https://github.com/bids-standard/pybids/tree/master/bids/layout/config
    """
    default = "config_pybids.json"
    return get_config(config_file, default)


def get_bids_filter_config(config_file: Path = None) -> dict:
    """Load the bids filter file config.

    Args:
        config_file (Path, optional): Config to load. Defaults to None.

    Returns:
        dict: _description_
    """
    default = "default_filter_file.json"
    return get_config(config_file, default)


def get_config(config_file: Path = None, default: str = "") -> dict:
    """Load a config stored in a JSON.

    Args:
        config_file (str, optional): File to load. Defaults to None.
        Will look into the config directory if None.

        default (str, optional): Default file to load. Defaults to "".

    Returns:
        dict: Config as a dictionary.

    """
    if config_file is None or not Path(config_file).exists():
        my_path = Path(__file__).resolve().parent
        config_file = my_path.joinpath(default)

    if config_file is None or not Path(config_file).exists():
        raise FileNotFoundError(f"Config file {config_file} not found")

    with open(config_file, "r") as ff:
        return json.load(ff)


def create_bidsname(
    layout: BIDSLayout, filename: Union[dict, Path], filetype: str
) -> Path:
    """Return a BIDS valid filename for layout and a filename or a dict of BIDS entities.

    Args:
        layout (BIDSLayout): BIDSLayout of the dataset.

        filename (Union[dict, Path]): Dictonary of BIDS entities or a Path to a file.

        filetype (str): One of the file type available in the BIDS name config.

    Returns:
        Path: _description_
    """
    if isinstance(filename, dict):
        entities = filename
    else:
        entities = layout.parse_file_entities(filename)

    bids_name_config = get_bidsname_config()

    output_file = layout.build_path(entities, bids_name_config[filetype], validate=False)

    output_file = Path(layout.root).joinpath(output_file)

    return output_file.resolve()


def check_layout(layout: BIDSLayout) -> None:
    """_summary_.

    Args:
        layout (BIDSLayout): BIDSLayout of the dataset.

    Raises:
        Exception: _description_

        Exception: _description_
    """
    desc = layout.get_dataset_description()
    if desc["DatasetType"] != "derivative":
        raise Exception("Input dataset should be BIDS derivative")

    cfg = config()

    bf = layout.get(
        return_type="filename",
        task=cfg["task"],
        space=cfg["space"],
        suffix="^bold$",
        extension="nii.*",
        regex_search=True,
    )

    generated_by = desc["GeneratedBy"][0]["Name"]
    if generated_by.lower() == "bidsmreye":
        bf = layout.get(
            return_type="filename",
            task=cfg["task"],
            space=cfg["space"],
            suffix="^mask$",
            extension="p",
            regex_search=True,
        )

    if bf == []:
        raise Exception("Input dataset does not have any data to process")
