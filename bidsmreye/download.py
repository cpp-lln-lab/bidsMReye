"""Download the models from OSF."""

from __future__ import annotations

import warnings
from importlib import resources
from pathlib import Path

import pooch

import bidsmreye
from bidsmreye.defaults import available_models, default_model
from bidsmreye.logging import bidsmreye_log

log = bidsmreye_log(name="bidsmreye")


def download(
    model: str | Path | None = None, output_dir: Path | str | None = None
) -> Path | None:
    """Download the models from OSF.

    :param model: Model to download. defaults to None
    :type model: str, optional

    :param output_dir: Path where to save the model. Defaults to None.
    :type output_dir: Path, optional

    :return: Path to the downloaded model.
    :rtype: Path
    """
    if not model:
        model = default_model()
    if isinstance(model, Path):
        assert model.is_file()
        return model.absolute()
    if model not in available_models():
        warnings.warn(f"{model} is not a valid model name.", stacklevel=3)
        return None

    if output_dir is None:
        output_dir = Path.cwd() / "models"
    if isinstance(output_dir, str):
        output_dir = Path(output_dir)

    POOCH = pooch.create(
        path=output_dir,
        base_url="https://osf.io/download/",
        registry=None,
    )
    source = resources.files(bidsmreye) / "models" / "registry.txt"
    with resources.as_file(source) as registry_file:
        POOCH.load_registry(registry_file)

    output_file = output_dir / f"dataset_{model}"

    if not output_file.is_file():
        file_idx = available_models().index(model)
        filename = f"dataset_{available_models()[file_idx]}.h5"
        output_file = POOCH.fetch(filename, progressbar=True)
        if isinstance(output_file, str):
            output_file = Path(output_file)

    else:
        log.info(f"{output_file} already exists.")

    return output_file
