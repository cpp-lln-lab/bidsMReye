import json
from os.path import abspath
from os.path import dirname
from os.path import join
from pathlib import Path


def write_dataset_description(layout):

    output_file = join(layout.root, "dataset_description.json")

    with open(output_file, "w") as ff:
        json.dump(layout.dataset_description, ff)


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

    But they don't cover the ``ephys`` so we are using modified config, that
    should cover both ephys and microscopy.

    TODO the "default_path_patterns" of that config has not been extended for
    ephys or microscopy yet
    """
    default = "config_pybids.json"
    return get_config(config_file, default)


def get_config(config_file="", default="") -> dict:

    if config_file == "" or not Path(config_file).exists():
        my_path = dirname(abspath(__file__))
        config_file = join(my_path, default)

    if config_file == "" or not Path(config_file).exists():
        return
    with open(config_file, "r") as ff:
        return json.load(ff)


def create_bidsname(layout, filename: str, filetype: str) -> str:

    entities = layout.parse_file_entities(filename)

    bids_name_config = get_bidsname_config()
    output_file = layout.build_path(entities, bids_name_config[filetype], validate=False)

    output_file = abspath(join(layout.root, output_file))

    return output_file
