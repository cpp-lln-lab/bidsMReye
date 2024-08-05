"""Define the command line interface."""

from __future__ import annotations

import sys
from typing import Any

from rich_argparse import RichHelpFormatter

from bidsmreye._parsers import common_parser, download_parser
from bidsmreye.bidsmreye import bidsmreye
from bidsmreye.defaults import default_log_level, log_levels
from bidsmreye.download import download
from bidsmreye.logging import bidsmreye_log

log = bidsmreye_log(name="bidsmreye")


def cli(argv: Any = sys.argv) -> None:
    """Run the bids app.

    :param argv: _description_, defaults to sys.argv
    :type argv: _type_, optional
    """
    parser = common_parser(formatter_class=RichHelpFormatter)

    args = parser.parse_args(argv[1:])

    log.debug(f"args:\n{args}")

    # TODO integrate as part of base config
    # https://stackoverflow.com/a/53293042/14223310
    log_level = log_levels().index(default_log_level())
    # For each "-v" flag, adjust the logging verbosity accordingly
    # making sure to clamp off the value from 0 to 4, inclusive of both
    for adjustment in args.log_level or ():
        log_level = min(len(log_levels()) - 1, max(log_level + adjustment, 0))
    log_level_name = log_levels()[log_level]

    model_weights_file = None
    if getattr(args, "model", None) is not None:
        model_weights_file = str(getattr(args, "model"))  # noqa: B009

    bidsmreye(
        bids_dir=args.bids_dir[0],
        output_dir=args.output_dir[0],
        analysis_level=args.analysis_level[0],
        action=args.command,
        participant_label=args.participant_label or None,
        space=args.space or None,
        task=args.task or None,
        run=args.run or None,
        debug=args.debug,
        model_weights_file=model_weights_file,
        reset_database=args.reset_database,
        bids_filter_file=args.bids_filter_file,
        non_linear_coreg=bool(getattr(args, "non_linear_coreg", False)),
        log_level_name=log_level_name,
        force=bool(getattr(args, "force", False)),
    )


def cli_download(argv: Any = sys.argv) -> None:
    """Download the models from OSF.

    :return: _description_
    :rtype: _type_
    """
    parser = download_parser(formatter_class=RichHelpFormatter)
    args = parser.parse_args(argv[1:])

    download(model=args.model, output_dir=args.output_dir)
