import json
from os.path import abspath
from os.path import dirname
from os.path import join
from pathlib import Path

from bids import BIDSLayout

from .utils import create_dir_if_absent


def get_dataset_layout(dataset_path: str, config={}):

    create_dir_if_absent(dataset_path)

    if config == {}:
        pybids_config = get_pybids_config()

    return BIDSLayout(
        dataset_path, validate=False, derivatives=False, config=pybids_config
    )


def write_dataset_description(layout):

    output_file = join(layout.root, "dataset_description.json")

    with open(output_file, "w") as ff:
        json.dump(layout.dataset_description, ff, indent=4)


def set_dataset_description(layout, is_derivative=True):

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
    layout_out = get_dataset_layout(output_location)
    layout_out = set_dataset_description(layout_out)
    layout_out.dataset_description["DatasetType"] = "derivative"
    layout_out.dataset_description["GeneratedBy"][0]["Name"] = "bidsNighres"
    write_dataset_description(layout_out)
    return layout_out


def get_bidsname_config(config_file="") -> dict:
    """
    See the Path construction demo in the pybids tuto
    https://github.com/bids-standard/pybids/blob/master/examples/pybids_tutorial.ipynb
    """
    default = "config_bidsname.json"
    return get_config(config_file, default)


def get_pybids_config(config_file="") -> dict:
    """
    Pybids configs are stored in the layout module
    https://github.com/bids-standard/pybids/tree/master/bids/layout/config
    """
    default = "config_pybids.json"
    return get_config(config_file, default)


def get_bids_filter_config(config_file="") -> dict:
    default = "default_filter_file.json"
    return get_config(config_file, default)


def get_config(config_file="", default="") -> dict:

    if config_file == "" or not Path(config_file).exists():
        my_path = dirname(abspath(__file__))
        config_file = join(my_path, default)

    if config_file == "" or not Path(config_file).exists():
        return
    with open(config_file, "r") as ff:
        return json.load(ff)


def create_bidsname(layout, filename, filetype: str) -> str:
    """[summary]

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
    output_file = layout.build_path(entities, bids_name_config[filetype], validate=False)

    output_file = abspath(join(layout.root, output_file))

    return output_file


def check_layout(layout):

    bf = layout.get(
        return_type="filename",
        suffix="^MP2RAGE$",
        extension="nii.*",
        regex_search=True,
    )

    if bf == []:
        raise Exception("Input dataset does not have any data to process")
