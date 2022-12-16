#!/usr/bin/env python
"""Main script."""
from __future__ import annotations

import argparse
import sys
from typing import Any
from typing import IO

import rich

from . import _version
from bidsmreye.download import download
from bidsmreye.generalize import generalize
from bidsmreye.prepare_data import prepare_data
from bidsmreye.utils import available_models
from bidsmreye.utils import bidsmreye_log
from bidsmreye.utils import Config
from bidsmreye.utils import default_log_level
from bidsmreye.utils import default_model
from bidsmreye.utils import log_levels

__version__ = _version.get_versions()["version"]

log = bidsmreye_log(name="bidsmreye")


def cli(argv: Any = sys.argv) -> None:
    """Run the bids app.

    :param argv: _description_, defaults to sys.argv
    :type argv: _type_, optional
    """
    parser = common_parser()

    args = parser.parse_args(argv[1:])

    model_weights_file = args.model or None

    cfg = Config(
        args.bids_dir,
        args.output_dir,
        participant=args.participant_label or None,
        space=args.space or None,
        task=args.task or None,
        run=args.run or None,
        debug=args.debug,
        model_weights_file=model_weights_file,
        reset_database=args.reset_database,
        bids_filter=args.bids_filter_file,
        non_linear_coreg=args.non_linear_coreg,
    )  # type: ignore

    # TODO integrate as part of base config
    # https://stackoverflow.com/a/53293042/14223310
    log_level = log_levels().index(default_log_level())
    # For each "-v" flag, adjust the logging verbosity accordingly
    # making sure to clamp off the value from 0 to 4, inclusive of both
    for adjustment in args.log_level or ():
        log_level = min(len(log_levels()) - 1, max(log_level + adjustment, 0))
    log_level_name = log_levels()[log_level]
    log.setLevel(log_level_name)

    log.info("Running bidsmreye version %s", __version__)

    if cfg.debug:
        log.debug("DEBUG MODE")

    log.debug(f"args:\n{args}")
    log.debug(f"Configuration:\n{cfg}")

    if args.action in ["all", "generalize"] and isinstance(cfg.model_weights_file, str):
        cfg.model_weights_file = download(cfg.model_weights_file)

    if args.analysis_level == "participant":

        if args.action == "all":
            prepare_data(cfg)
            generalize(cfg)

        elif args.action == "prepare":
            prepare_data(cfg)

        elif args.action == "generalize":
            generalize(cfg)

        else:
            log.error("Unknown action")
            sys.exit(1)


class MuhParser(argparse.ArgumentParser):
    """Parser for the main script."""

    def _print_message(self, message: str, file: IO[str] | None = None) -> None:
        rich.print(message, file=file)


def common_parser() -> MuhParser:
    """Execute the main script."""
    parser = MuhParser(
        description="BIDS app using deepMReye to decode eye motion for fMRI time series data.",
        epilog="""
        For a more readable version of this help section,
        see the online https://bidsmreye.readthedocs.io/.
        """,
    )
    parser.add_argument(
        "bids_dir",
        help="""
        The directory with the input dataset formatted according to the BIDS standard.
        """,
    )
    parser.add_argument(
        "output_dir",
        help="""
        The directory where the output files will be stored.
        """,
    )
    parser.add_argument(
        "analysis_level",
        help="""Level of the analysis that will be performed.
        Multiple participant level analyses can be run independently (in parallel)
        using the same output_dir.
        """,
        choices=["participant"],
        default="participant",
    )
    parser.add_argument(
        "--action",
        help="""
        What action to perform.
        """,
        choices=["all", "prepare", "generalize"],
        default="all",
    )
    parser.add_argument(
        "--participant_label",
        help="""
        The label(s) of the participant(s) that should be analyzed.
        The label corresponds to sub-<participant_label> from the BIDS spec
        (so it does not include "sub-").

        If this parameter is not provided, all subjects will be analyzed.
        Multiple participants can be specified with a space separated list.
        """,
        nargs="+",
    )
    parser.add_argument(
        "--task",
        help="""
        The label of the task that will be analyzed.

        The label corresponds to task-<task_label> from the BIDS spec
        so it does not include "task-").
        """,
        nargs="+",
    )
    parser.add_argument(
        "--run",
        help="""
        The label of the run that will be analyzed.

        The label corresponds to run-<task_label> from the BIDS spec
        so it does not include "run-").
        """,
        nargs="+",
    )
    parser.add_argument(
        "--space",
        help="""
        The label of the space that will be analyzed.

        The label corresponds to space-<space_label> from the BIDS spec
        (so it does not include "space-").
        """,
        nargs="+",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="log_level",
        action="append_const",
        const=-1,
    )
    parser.add_argument("--debug", help="Switch to debug mode", action="store_true")
    parser.add_argument(
        "--reset_database",
        help="""
        Resets the database of the input dataset.
        """,
        action="store_true",
    )
    parser.add_argument(
        "--bids_filter_file",
        help="""
        A JSON file describing custom BIDS input filters using PyBIDS.
        For further details, please check out TBD.
        """,
    )
    parser.add_argument(
        "--version",
        action="version",
        help="show program's version number and exit",
        version=f"\nbidsMReye version {__version__}\n",
    )
    # TODO make it possible to pass path to a model ?
    prepare_only = parser.add_argument_group("prepare only arguments")
    prepare_only.add_argument(
        "--non_linear_coreg",
        help="""
        Uses a more aggressive (and non-linear) alignment procedure to the deepmreye template.
        """,
        action="store_true",
    )
    # TODO make it possible to pass path to a model ?
    generalize_only = parser.add_argument_group("generalize only arguments")
    generalize_only.add_argument(
        "--model",
        help="model to use",
        choices=available_models(),
        default=default_model(),
    )

    return parser


def args_to_dict(args: argparse.Namespace) -> dict[str, Any]:
    """Converts a argparse.Namespace object to a dictionary."""
    return vars(args)
