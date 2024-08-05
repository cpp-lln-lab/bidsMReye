#!/usr/bin/env python
"""Main script."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from bidsmreye._version import __version__
from bidsmreye.configuration import Config
from bidsmreye.defaults import default_log_level
from bidsmreye.logging import bidsmreye_log

log = bidsmreye_log(name="bidsmreye")


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
    force: bool = False,
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
        force=force,
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
    log.debug(f"{analysis_level=} {action=}")

    if action in {"all", "generalize"} and isinstance(cfg.model_weights_file, str):
        from bidsmreye.download import download

        model_output_dir = cfg.output_dir / "models"
        model_output_dir.mkdir(exist_ok=True, parents=True)

        cfg.model_weights_file = download(
            cfg.model_weights_file, output_dir=model_output_dir
        )

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
