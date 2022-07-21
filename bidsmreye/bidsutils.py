"""foo."""
import json
from os.path import abspath
from os.path import dirname
from os.path import join
from pathlib import Path

from bids import BIDSLayout
from rich import print

from bidsmreye.utils import config
from bidsmreye.utils import create_dir_if_absent


def get_dataset_layout(dataset_path: str, config={}):
    """_summary_.

    Args:
        dataset_path (str): _description_
        config (dict, optional): _description_. Defaults to {}.

    Returns:
        _type_: _description_
    """
    create_dir_if_absent(dataset_path)

    if config == {}:
        pybids_config = get_pybids_config()

    return BIDSLayout(
        dataset_path, validate=False, derivatives=False, config=pybids_config
    )


def write_dataset_description(layout):
    """_summary_.

    Args:
        layout (_type_): _description_
    """
    output_file = join(layout.root, "dataset_description.json")

    with open(output_file, "w") as ff:
        json.dump(layout.dataset_description, ff, indent=4)


def set_dataset_description(layout, is_derivative=True):
    """_summary_.

    Args:
        layout (_type_): _description_
        is_derivative (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
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


def init_derivatives_layout(output_location):
    """_summary_.

    Args:
        output_location (_type_): _description_

    Returns:
        _type_: _description_
    """
    layout_out = get_dataset_layout(output_location)
    layout_out = set_dataset_description(layout_out)
    layout_out.dataset_description["DatasetType"] = "derivative"
    layout_out.dataset_description["GeneratedBy"][0]["Name"] = "bidsmreye"
    write_dataset_description(layout_out)
    return layout_out


def get_bidsname_config(config_file="") -> dict:
    """
    See the Path construction demo in the pybids tutorial.

    https://github.com/bids-standard/pybids/blob/master/examples/pybids_tutorial.ipynb
    """
    default = "config_bidsname.json"
    return get_config(config_file, default)


def get_pybids_config(config_file="") -> dict:
    """
    Pybids configs are stored in the layout module.

    https://github.com/bids-standard/pybids/tree/master/bids/layout/config
    """
    default = "config_pybids.json"
    return get_config(config_file, default)


def get_bids_filter_config(config_file="") -> dict:
    """_summary_.

    Args:
        config_file (str, optional): _description_. Defaults to "".

    Returns:
        dict: _description_
    """
    default = "default_filter_file.json"
    return get_config(config_file, default)


def get_config(config_file="", default="") -> dict:
    """_summary_.

    Args:
        config_file (str, optional): _description_. Defaults to "".
        default (str, optional): _description_. Defaults to "".

    Returns:
        dict: _description_
    """
    if config_file == "" or not Path(config_file).exists():
        my_path = dirname(abspath(__file__))
        config_file = join(my_path, default)

    if config_file == "" or not Path(config_file).exists():
        return
    with open(config_file, "r") as ff:
        return json.load(ff)


def create_bidsname(layout, filename, filetype: str) -> str:
    """[summary].

    Args:
        layout ([type]): [description]
        filename ([type]): [description]
        filetype (str): [description]

    Returns:
        str: [description]
    """
    # filename is path or entities dict

    if isinstance(filename, str):
        entities = layout.parse_file_entities(filename)
    else:
        entities = filename

    bids_name_config = get_bidsname_config()

    print(bids_name_config)
    print(entities)

    output_file = layout.build_path(entities, bids_name_config[filetype], validate=False)

    output_file = abspath(join(layout.root, output_file))

    return output_file


def check_layout(layout):
    """_summary_.

    Args:
        layout (_type_): _description_

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
