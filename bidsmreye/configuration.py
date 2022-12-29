from __future__ import annotations

import json
import os
import warnings
from pathlib import Path
from typing import Any

from attrs import asdict
from attrs import converters
from attrs import define
from attrs import field
from bids import BIDSLayout  # type: ignore

from bidsmreye.logging import bidsmreye_log

log = bidsmreye_log(name="bidsmreye")


@define
class Config:
    """Set up config and check that all required fields are set.

    :raises ValueError: _description_
    :raises RuntimeError: _description_

    :return: _description_
    :rtype: _type_
    """

    input_dir = field(default=None, converter=Path)

    @input_dir.validator
    def _check_input_dir(self, attribute: str, value: Path) -> None:
        if not value.is_dir:  # type: ignore
            raise ValueError(
                f"input_dir must be an existing directory:\n{value.resolve()}."
            )

        if not value.joinpath("dataset_description.json").is_file():
            raise ValueError(
                f"""input_dir does not seem to be a valid BIDS dataset.
No dataset_description.json found:
\t{value.resolve()}."""
            )

    output_dir: Path = field(default=None, converter=Path)

    subjects: Any | None = field(kw_only=True, default=None)

    space: Any | None = field(kw_only=True, default=None)
    task: Any | None = field(kw_only=True, default=None)
    run: Any | None = field(kw_only=True, default=None)

    model_weights_file: str | Path | None = field(kw_only=True, default=None)
    bids_filter: Any = field(kw_only=True, default=None)

    debug: str | bool | None = field(kw_only=True, default=None)
    reset_database: str | bool | None = field(kw_only=True, default=None)
    non_linear_coreg: bool = field(kw_only=True, default=False)

    has_GPU: bool = False

    def __attrs_post_init__(self) -> None:
        """Check that output_dir exists and gets info from layout if not specified."""
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

        self.output_dir = self.output_dir.joinpath("bidsmreye")
        if not self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)

        database_path = self.input_dir.joinpath("pybids_db")

        layout_in = BIDSLayout(
            self.input_dir,
            validate=False,
            derivatives=False,
            database_path=database_path,
            reset_database=self.reset_database,
        )

        log.debug(f"Layout in:\n{layout_in}")

        if not database_path.is_dir():
            layout_in.save(database_path)

        self.check_argument(attribute="subjects", layout_in=layout_in)
        self.check_argument(attribute="task", layout_in=layout_in)
        self.check_argument(attribute="run", layout_in=layout_in)
        self.check_argument(attribute="space", layout_in=layout_in)

    def check_argument(self, attribute: str, layout_in: BIDSLayout) -> Config:
        """Check an attribute value compared to the input dataset content.

        :param attribute:
        :type  attribute: str

        :param layout_in:
        :type  layout_in: BIDSLayout

        :raises RuntimeError:

        :return:
        :rtype: Config
        """
        if attribute == "subjects":
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
                    f"{attribute}(s) {missing_values} not found in {self.input_dir}"
                )
            value = list(set(getattr(self, attribute)) & set(value))

        setattr(self, attribute, value)

        # run and space can be empty if their entity are not used
        if attribute not in ["run", "space"] and not getattr(self, attribute):
            raise RuntimeError(f"No {attribute} found in {self.input_dir}")

        return self

    def listify(self, attribute: str) -> Config:
        """Convert attribute to list if not already."""
        if getattr(self, attribute) and not isinstance(getattr(self, attribute), list):
            setattr(self, attribute, [getattr(self, attribute)])

        return self


def config_to_dict(cfg: Config) -> dict[str, Any]:
    """Convert a config to a dictionary.

    :param cfg:
    :type  cfg: _type_

    :return:
    :rtype: _type_
    """
    dict_cfg = asdict(cfg)
    for key, value in dict_cfg.items():
        if isinstance(value, Path):
            dict_cfg[key] = str(value)
    return dict_cfg


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
