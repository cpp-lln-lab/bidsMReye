from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bids import BIDSLayout  # type: ignore

from . import _version
from bidsmreye.configuration import Config
from bidsmreye.configuration import config_to_dict
from bidsmreye.configuration import get_bids_filter_config
from bidsmreye.configuration import get_bidsname_config
from bidsmreye.configuration import get_pybids_config
from bidsmreye.logging import bidsmreye_log
from bidsmreye.methods import methods
from bidsmreye.utils import copy_license
from bidsmreye.utils import create_dir_if_absent

log = bidsmreye_log("bidsmreye")

__version__ = _version.get_versions()["version"]


def check_layout(cfg: Config, layout: BIDSLayout, for_file: str = "bold") -> None:
    """Check layout.

    :param cfg: Configuration object
    :type  cfg: Config

    :param layout: BIDSLayout of the dataset.
    :type  layout: BIDSLayout

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

    this_filter = get_bids_filter_config()[for_file]

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


def create_sidecar(
    layout: BIDSLayout, filename: str, SamplingFrequency: float | None = None
) -> None:
    """Create sidecar for the eye motion timeseries."""
    if SamplingFrequency is None:
        SamplingFrequency = 0
    content = {
        "SamplingFrequency": SamplingFrequency,
    }
    sidecar_name = create_bidsname(layout, filename, "confounds_json")
    json.dump(content, open(sidecar_name, "w"), indent=4)


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

    dataset_path = dataset_path.resolve()

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


def init_dataset(cfg: Config, qc_only: bool = False) -> BIDSLayout:

    layout_out = init_derivatives_layout(cfg)

    citation_file = methods(cfg.output_dir, qc_only=qc_only)
    log.info(f"Method section generated: {citation_file}")

    license_file = copy_license(cfg.output_dir)
    log.info(f"License file added: {license_file}")

    return layout_out


def init_derivatives_layout(cfg: Config) -> BIDSLayout:
    """Initialize a derivatives dataset and returns its layout.

    :param output_dir:
    :type output_dir: Path

    :return:
    :rtype: BIDSLayout
    """
    create_dir_if_absent(cfg.output_dir)
    layout_out = get_dataset_layout(cfg.output_dir)
    layout_out = set_dataset_description(layout_out)
    layout_out.dataset_description["DatasetType"] = "derivative"
    layout_out.dataset_description["GeneratedBy"][0]["Name"] = "bidsmreye"
    layout_out.dataset_description["GeneratedBy"][0]["config"] = config_to_dict(cfg)
    write_dataset_description(layout_out)
    return layout_out


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
    subjects = layout.get(return_type="id", target="subject", subject=cfg.subjects)

    if subjects == [] or subjects is None:
        raise RuntimeError(f"No subject found in layout:\n\t{layout.root}")

    if cfg.debug:
        subjects = [subjects[0]]
        log.debug("Running first subject only.")

    log.info(f"processing subjects: {subjects}")

    return subjects


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
        "BIDSVersion": "1.7.0",
        "DatasetType": "raw",
        "License": "CCO",
        "Authors": ["", ""],
        "Acknowledgements": "Special thanks to ",
        "HowToAcknowledge": """Please cite this paper: Frey, M., Nau, M. & Doeller, C.F.
Magnetic resonance-based eye tracking using deep neural networks.
Nat Neurosci 24, 1772-1779 (2021).
https://doi.org/10.1038/s41593-021-00947-w""",
        "Funding": ["", ""],
        "ReferencesAndLinks": ["https://doi.org/10.1038/s41593-021-00947-w"],
        "DatasetDOI": "doi:",
    }

    if is_derivative:
        data["GeneratedBy"] = [
            {
                "Name": "bidsMReye",
                "Version": __version__,
                "Container": {"Type": "", "Tag": ""},
                "Description": "",
                "CodeURL": "https://github.com/cpp-lln-lab/bidsMReye.git",
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


def write_dataset_description(layout: BIDSLayout) -> None:
    """Add a dataset_description.json to a BIDS dataset.

    :param layout: BIDSLayout of the dataset to update.
    :type layout: BIDSLayout
    """
    output_file = Path(layout.root).joinpath("dataset_description.json")

    with open(output_file, "w") as ff:
        json.dump(layout.dataset_description, ff, indent=4)
