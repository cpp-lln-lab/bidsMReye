#!/usr/bin/env python
"""Main script."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from rich_argparse import RichHelpFormatter

from bidsmreye._parsers import common_parser
from bidsmreye._version import __version__
from bidsmreye.configuration import Config
from bidsmreye.defaults import default_log_level, log_levels
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

    bidsmreye(
        bids_dir=args.bids_dir,
        output_dir=args.output_dir,
        analysis_level=args.analysis_level,
        action=args.action,
        participant_label=args.participant_label or None,
        space=args.space or None,
        task=args.task or None,
        run=args.run or None,
        debug=args.debug,
        model_weights_file=args.model or None,
        reset_database=args.reset_database,
        bids_filter_file=args.bids_filter_file,
        non_linear_coreg=args.non_linear_coreg,
        log_level_name=log_level_name,
    )


def bidsmreye(
    bids_dir: str,
    output_dir: str,
    analysis_level: str,
    action: str,
    participant_label: list[str] | None = None,
    space: list[str] | None = None,
    task: list[str] | None = None,
    run: list[str] | None = None,
    debug: bool | None = None,
    model_weights_file: str | None = None,
    reset_database: bool | None = None,
    bids_filter_file: str | None = None,
    non_linear_coreg: bool = False,
    log_level_name: str | None = None,
) -> None:
    bids_filter = None
    if bids_filter_file is not None and Path(bids_filter_file).is_file():
        with open(Path(bids_filter_file)) as f:
            bids_filter = json.load(f)

    if reset_database is None:
        reset_database = False

    cfg = Config(
        bids_dir,
        output_dir,
        subjects=participant_label or None,
        space=space or None,
        task=task or None,
        run=run or None,
        debug=debug,
        model_weights_file=model_weights_file,
        reset_database=reset_database,
        bids_filter=bids_filter,
        non_linear_coreg=non_linear_coreg,
    )  # type: ignore

    if log_level_name is None:
        log_level_name = default_log_level()
    log.setLevel(log_level_name)

    print(log_level_name)

    log.warning(
        f"log level: {log_level_name}",
    )

    log.info(f"Running bidsmreye version {__version__}")

    if cfg.debug:
        log.debug("DEBUG MODE")

    log.debug(f"Configuration:\n{cfg}")

    if action in {"all", "generalize"} and isinstance(cfg.model_weights_file, str):
        from bidsmreye.download import download

        cfg.model_weights_file = download(cfg.model_weights_file)

    dispatch(analysis_level=analysis_level, action=action, cfg=cfg)


def dispatch(analysis_level: str, action: str, cfg: Config) -> None:
    if analysis_level == "group":
        if action == "qc":
            from bidsmreye.visualize import group_report

            group_report(cfg=cfg)
        else:
            log.error("Unknown group level action")
            sys.exit(1)

    elif analysis_level == "participant":
        if action == "all":
            from bidsmreye.generalize import generalize
            from bidsmreye.prepare_data import prepare_data

            prepare_data(cfg)
            generalize(cfg)
        elif action == "prepare":
            from bidsmreye.prepare_data import prepare_data

            prepare_data(cfg)
        elif action == "generalize":
            from bidsmreye.generalize import generalize

            generalize(cfg)
        elif action == "qc":
            from bidsmreye.quality_control import quality_control_input

            quality_control_input(cfg)
        else:
            log.error("Unknown participant level action")
            sys.exit(1)
