import multiprocessing
import shutil
from pathlib import Path

from bidsmreye.configuration import Config
from bidsmreye.database import (
    DATABASE_FILE,
    get_database_path,
    get_layout_with_database,
)

EXPECTED_SUBJECTS = ["01", "02", "03", "04", "05"]


def test_get_database_path(tmp_path):
    work_dir = tmp_path / "work"

    path = get_database_path(work_dir, tmp_path / "ds" / "fmriprep")

    assert path.parent == work_dir / "pybids_db"
    assert path.name.startswith("fmriprep_")
    # deterministic
    assert path == get_database_path(work_dir, tmp_path / "ds" / "fmriprep")
    # different datasets with the same name do not share a database
    assert path != get_database_path(work_dir, tmp_path / "other" / "fmriprep")


def _leftover_tmp_dirs(database_path: Path) -> list[Path]:
    return [
        p
        for p in database_path.parent.iterdir()
        if p.name.endswith(".tmp") or p.name.endswith(".old")
    ]


def test_get_layout_with_database(tmp_path, pybids_test_dataset):
    database_path = tmp_path / "pybids_db" / "fmriprep"

    layout = get_layout_with_database(pybids_test_dataset, database_path)

    assert sorted(layout.get_subjects()) == EXPECTED_SUBJECTS
    assert (database_path / DATABASE_FILE).is_file()
    assert _leftover_tmp_dirs(database_path) == []

    # second call loads the database
    layout = get_layout_with_database(pybids_test_dataset, database_path)
    assert sorted(layout.get_subjects()) == EXPECTED_SUBJECTS


def test_get_layout_with_database_reset(tmp_path, pybids_test_dataset):
    dataset = tmp_path / "fmriprep"
    shutil.copytree(pybids_test_dataset, dataset)
    database_path = tmp_path / "pybids_db" / "fmriprep"

    get_layout_with_database(dataset, database_path)

    shutil.rmtree(dataset / "sub-05")

    # without reset: the database is stale
    layout = get_layout_with_database(dataset, database_path)
    assert "05" in layout.get_subjects()

    layout = get_layout_with_database(dataset, database_path, reset_database=True)
    assert "05" not in layout.get_subjects()
    # and the new index was saved
    layout = get_layout_with_database(dataset, database_path)
    assert "05" not in layout.get_subjects()
    assert _leftover_tmp_dirs(database_path) == []


def _index_subjects(args: tuple[str, str, bool]) -> list[str]:
    dataset, database_path, reset_database = args
    layout = get_layout_with_database(
        dataset, database_path, reset_database=reset_database
    )
    return sorted(layout.get_subjects())


def test_get_layout_with_database_parallel(tmp_path, pybids_test_dataset):
    """Processes started at the same time must all see the full dataset.

    Regression test for https://github.com/cpp-lln-lab/bidsMReye/issues/170
    """
    database_path = tmp_path / "pybids_db" / "fmriprep"
    n_processes = 8

    for reset_database in [False, True]:
        args = [(str(pybids_test_dataset), str(database_path), reset_database)]
        with multiprocessing.get_context("spawn").Pool(n_processes) as pool:
            results = pool.map(_index_subjects, args * n_processes)

        assert all(subjects == EXPECTED_SUBJECTS for subjects in results)
        assert (database_path / DATABASE_FILE).is_file()
        assert _leftover_tmp_dirs(database_path) == []


def test_config_work_dir_default(tmp_path, pybids_test_dataset):
    dataset = tmp_path / "fmriprep"
    # ignore databases that older versions saved in the input dataset
    shutil.copytree(
        pybids_test_dataset, dataset, ignore=shutil.ignore_patterns("pybids_db")
    )

    cfg = Config(dataset, tmp_path / "output")

    assert cfg.work_dir == (tmp_path / "output" / "work").absolute()
    database_path = get_database_path(cfg.work_dir, dataset)
    assert (database_path / DATABASE_FILE).is_file()
    # nothing written in the input dataset
    assert not (dataset / "pybids_db").exists()


def test_config_work_dir(tmp_path, pybids_test_dataset):
    cfg = Config(pybids_test_dataset, tmp_path / "output", work_dir=tmp_path / "work")

    assert cfg.work_dir == tmp_path / "work"
    database_path = get_database_path(tmp_path / "work", pybids_test_dataset)
    assert (database_path / DATABASE_FILE).is_file()
    assert not (tmp_path / "output" / "work").exists()
