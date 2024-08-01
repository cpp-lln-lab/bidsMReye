from __future__ import annotations

from argparse import ArgumentParser, HelpFormatter

from bidsmreye._version import __version__
from bidsmreye.defaults import allowed_actions, available_models, default_model


def common_parser(formatter_class: type[HelpFormatter] = HelpFormatter) -> ArgumentParser:
    """Execute the main script."""
    parser = ArgumentParser(
        description=(
            "BIDS app using deepMReye to decode " "eye motion for fMRI time series data."
        ),
        epilog="""
        For a more readable version of this help section,
        see the online https://bidsmreye.readthedocs.io/.
        """,
        formatter_class=formatter_class,
    )
    parser.add_argument(
        "bids_dir",
        help=(
            "The directory with the input dataset "
            "formatted according to the BIDS standard."
        ),
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
        choices=["participant", "group"],
        default="participant",
    )
    parser.add_argument(
        "--action",
        help="""
        What action to perform.
        """,
        choices=allowed_actions(),
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
        help="Uses a more aggressive (and non-linear) alignment procedure "
        "to the deepmreye template.",
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
