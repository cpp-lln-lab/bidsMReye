"""Manage the pybids database of the input dataset.

The database is stored in a working directory (not in the input dataset)
so it can be shared by several bidsmreye processes running in parallel
(for example one process per participant on a cluster).
"""

import hashlib
import shutil
import uuid
from pathlib import Path

from bids import BIDSLayout  # type: ignore

from bidsmreye.logger import bidsmreye_log

log = bidsmreye_log(name="bidsmreye")

INPUT_PYBIDS_CONFIG = ["bids", "derivatives"]

DATABASE_FILE = "layout_index.sqlite"


def get_database_path(work_dir: str | Path, dataset_path: str | Path) -> Path:
    """Return where to store the pybids database of a dataset in the working directory.

    The folder name includes a hash of the absolute path of the dataset,
    so several datasets can share the same working directory.

    :param work_dir: Working directory.
    :type work_dir: str | Path

    :param dataset_path: Root of the dataset to index.
    :type dataset_path: str | Path

    :return: Path to the folder containing the pybids database.
    :rtype: Path
    """
    dataset_path = Path(dataset_path).absolute()
    digest = hashlib.sha256(str(dataset_path).encode()).hexdigest()[:8]
    return Path(work_dir).absolute() / "pybids_db" / f"{dataset_path.name}_{digest}"


def database_exists(database_path: Path) -> bool:
    """Check if a database exists at that location.

    Do not use bids.layout.db.ConnectionManager.exists
    as it creates the database folder as a side effect.
    """
    return (database_path / DATABASE_FILE).is_file()


def get_layout_with_database(
    dataset_path: str | Path,
    database_path: str | Path,
    config: str | list[str] | dict[str, str] | None = None,
    reset_database: bool = False,
) -> BIDSLayout:
    """Return the layout of a dataset and save its index to a database.

    If the database already exists it is loaded,
    otherwise the dataset is indexed and the index is saved.

    Safe to use from several processes at the same time:
    the dataset is indexed in memory and saved to a temporary folder
    that is then renamed to its final location.
    Renaming is atomic, so other processes can never load
    a partially written database:
    they either see no database (and index the dataset themselves)
    or a complete one.

    :param dataset_path: Root of the dataset to index.
    :type dataset_path: str | Path

    :param database_path: Folder where to store the pybids database.
    :type database_path: str | Path

    :param config: Pybids config to use. Defaults to ``["bids", "derivatives"]``.
    :type config: str | list[str] | dict[str, str] | None, optional

    :param reset_database: Reindex the dataset even if a database exists.
    :type reset_database: bool, optional

    :return: Layout of the dataset.
    :rtype: BIDSLayout
    """
    dataset_path = Path(dataset_path).absolute()
    database_path = Path(database_path).absolute()
    if config is None:
        config = INPUT_PYBIDS_CONFIG

    if not reset_database and database_exists(database_path):
        log.debug(f"Loading pybids database:\n\t{database_path}")
        return BIDSLayout(
            dataset_path,
            validate=False,
            derivatives=False,
            config=config,
            database_path=database_path,
        )

    log.info(f"Indexing {dataset_path}")
    layout = BIDSLayout(dataset_path, validate=False, derivatives=False, config=config)

    database_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = database_path.with_name(f".{database_path.name}.{uuid.uuid4().hex}.tmp")
    layout.save(tmp_path, replace_connection=False)

    if reset_database and database_path.exists():
        # move the old database out of the way first:
        # renaming is atomic so other processes see either the old or no database
        old_path = database_path.with_name(
            f".{database_path.name}.{uuid.uuid4().hex}.old"
        )
        try:
            database_path.rename(old_path)
        except OSError:
            # already moved by another process
            pass
        else:
            shutil.rmtree(old_path, ignore_errors=True)

    try:
        tmp_path.rename(database_path)
        log.debug(f"Pybids database saved to:\n\t{database_path}")
    except OSError:
        # another process saved its database first: use that one
        log.debug(f"Pybids database already saved by another process:\n\t{database_path}")
        shutil.rmtree(tmp_path, ignore_errors=True)

    return layout
