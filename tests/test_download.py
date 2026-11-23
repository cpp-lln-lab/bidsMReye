import shutil
import warnings
from pathlib import Path

import pytest

from bidsmreye.download import download


def test_download(tmp_path):
    download(model="1_guided_fixations", output_dir=str(tmp_path))

    assert tmp_path.is_dir()
    assert (tmp_path / "dataset_1_guided_fixations.h5").is_file()


def test_download_basic():
    download()
    output_file = download()

    output_dir = Path.cwd() / "models"
    print(output_file)
    assert output_dir.is_dir()
    assert (output_dir / "dataset_1to6.h5").is_file()

    shutil.rmtree(output_dir)


def test_download_unknown_model():
    with pytest.warns(UserWarning):
        download(model="foo")


@pytest.mark.parametrize("as_str", [True, False])
def test_download_model_path(tmp_path, as_str):
    """A path to an existing model file is returned as is, nothing is downloaded.

    The CLI passes the model as a string.

    https://github.com/cpp-lln-lab/bidsMReye/issues/91
    """
    model_file = tmp_path / "my_model.h5"
    model_file.write_bytes(b"")
    output_dir = tmp_path / "models"

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        output_file = download(
            model=str(model_file) if as_str else model_file, output_dir=output_dir
        )

    assert output_file == model_file.absolute()
    assert not output_dir.exists()


def test_download_model_path_missing(tmp_path):
    with pytest.raises(FileNotFoundError, match=r"missing\.h5"):
        download(model=tmp_path / "missing.h5")
