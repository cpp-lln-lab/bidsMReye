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
from bidsmreye.utils import bidsmreye_log
from bidsmreye.utils import Config

__version__ = _version.get_versions()["version"]

log = bidsmreye_log(name="bidsmreye")


def main(argv: Any = sys.argv) -> None:
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
    )  # type: ignore

    log_level = "DEBUG" if cfg.debug else args.verbosity

    log.setLevel(log_level)

    log.info("Running bidsmreye version %s", __version__)

    if cfg.debug:
        log.debug("DEBUG MODE")

    log.debug(f"args:\n{args}")
    log.debug(f"Configuration:\n{cfg}")

    if args.action in ["all", "generalize"]:
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
        see the online https://bidsmreye.readthedocs.io/".
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
        What action to perform:

        - all:        run all steps

        - prepare:    prepare data for analysis coregister to template,
                      normalize and extract data

        - generalize: generalize from data to give predicted labels
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
        "--verbosity", help="INFO, WARNING.", choices=["INFO", "WARNING"], default="INFO"
    )
    parser.add_argument(
        "--debug", help="true or false.", choices=["true", "false"], default="false"
    )
    parser.add_argument(
        "--reset_database",
        help="""
        Resets the database of the input dataset.
        """,
        choices=["true", "false"],
        default="false",
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
    gen = parser.add_argument_group("generalize only arguments")
    gen.add_argument(
        "--model",
        help="model to use",
        choices=[
            "1_guided_fixations",
            "2_pursuit",
            "3_openclosed",
            "3_pursuit",
            "4_pursuit",
            "5_free_viewing",
        ],
        default="1_guided_fixations",
    )

    return parser


if __name__ == "__main__":
    main()
