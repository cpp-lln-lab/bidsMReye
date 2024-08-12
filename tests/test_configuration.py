from __future__ import annotations

import pytest

from bidsmreye.configuration import (
    Config,
    config_to_dict,
    get_bidsname_config,
    get_config,
    get_pybids_config,
)


def test_Config(data_dir, pybids_test_dataset):
    cfg = Config(
        pybids_test_dataset,
        data_dir,
    )
    assert not cfg.debug
    assert not cfg.linear_coreg
    assert cfg.input_dir == pybids_test_dataset
    assert cfg.output_dir == data_dir / "bidsmreye"
    assert sorted(cfg.subjects) == ["01", "02", "03", "04", "05"]
    assert sorted(cfg.task) == ["nback", "rest"]
    assert sorted(cfg.space) == ["MNI152NLin2009cAsym", "T1w"]


def test_config_to_dict_smoke(data_dir, pybids_test_dataset):
    cfg = Config(
        pybids_test_dataset,
        data_dir,
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


def test_missing_subject(data_dir, pybids_test_dataset):
    with pytest.warns(UserWarning):
        Config(
            pybids_test_dataset,
            data_dir,
            subjects=["01", "07"],
        )


def test_missing_task(data_dir, pybids_test_dataset):
    with pytest.warns(UserWarning):
        Config(
            pybids_test_dataset,
            data_dir,
            task=["auditory", "rest"],
        )


def test_no_subject(data_dir, pybids_test_dataset):
    with pytest.raises(RuntimeError):
        Config(
            pybids_test_dataset,
            data_dir,
            subjects=["99"],
        )


def test_no_task(data_dir, pybids_test_dataset):
    with pytest.raises(RuntimeError):
        Config(
            pybids_test_dataset,
            data_dir,
            task=["foo"],
        )


def test_missing_space(data_dir, pybids_test_dataset):
    with pytest.warns(UserWarning):
        Config(
            pybids_test_dataset,
            data_dir,
            space=["T1w", "T2w"],
        )


def test_task_omit_missing_values(data_dir, pybids_test_dataset):
    cfg = Config(
        pybids_test_dataset,
        data_dir,
        task=["auditory", "rest"],
        subjects=["01", "07"],
        space=["T1w", "T2w"],
    )
    assert cfg.subjects == ["01"]
    assert cfg.task == ["rest"]
    assert cfg.space == ["T1w"]
