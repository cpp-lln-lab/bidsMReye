from __future__ import annotations

from pathlib import Path

import pytest

from bidsmreye.configuration import (
    Config,
    config_to_dict,
    get_bidsname_config,
    get_config,
    get_pybids_config,
)

from .utils import pybids_test_dataset


def test_Config():
    cfg = Config(
        pybids_test_dataset(),
        Path(__file__).parent.joinpath("data"),
    )
    assert not cfg.debug
    assert not cfg.non_linear_coreg
    assert cfg.input_dir == pybids_test_dataset()
    assert cfg.output_dir == Path(__file__).parent.joinpath("data", "bidsmreye")
    assert sorted(cfg.subjects) == ["01", "02", "03", "04", "05"]
    assert sorted(cfg.task) == ["nback", "rest"]
    assert sorted(cfg.space) == ["MNI152NLin2009cAsym", "T1w"]


def test_config_to_dict_smoke():
    cfg = Config(
        pybids_test_dataset(),
        Path(__file__).parent.joinpath("data"),
    )
    config_to_dict(cfg)


def test_get_config_error():
    with pytest.raises(FileNotFoundError):
        get_config("", "foo.json")


def test_get_bidsname_config_smoke():
    cfg = get_bidsname_config()
    assert cfg is not None


def test_get_pybids_config_smoke():
    cfg = get_pybids_config()
    assert cfg is not None


def test_missing_subject():
    with pytest.warns(UserWarning):
        Config(
            pybids_test_dataset(),
            Path(__file__).parent.joinpath("data"),
            subjects=["01", "07"],
        )


def test_missing_task():
    with pytest.warns(UserWarning):
        Config(
            pybids_test_dataset(),
            Path(__file__).parent.joinpath("data"),
            task=["auditory", "rest"],
        )


def test_no_subject():
    with pytest.raises(RuntimeError):
        Config(
            pybids_test_dataset(),
            Path(__file__).parent.joinpath("data"),
            subjects=["99"],
        )


def test_no_task():
    with pytest.raises(RuntimeError):
        Config(
            pybids_test_dataset(),
            Path(__file__).parent.joinpath("data"),
            task=["foo"],
        )


def test_missing_space():
    with pytest.warns(UserWarning):
        Config(
            pybids_test_dataset(),
            Path(__file__).parent.joinpath("data"),
            space=["T1w", "T2w"],
        )


def test_task_omit_missing_values():
    cfg = Config(
        pybids_test_dataset(),
        Path(__file__).parent.joinpath("data"),
        task=["auditory", "rest"],
        subjects=["01", "07"],
        space=["T1w", "T2w"],
    )
    assert cfg.subjects == ["01"]
    assert cfg.task == ["rest"]
    assert cfg.space == ["T1w"]
