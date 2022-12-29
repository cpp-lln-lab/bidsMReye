"""Write method section."""
from __future__ import annotations

import shutil
import warnings
from pathlib import Path

import chevron

from . import _version
from bidsmreye.defaults import available_models
from bidsmreye.defaults import default_model
from bidsmreye.utils import create_dir_for_file


__version__ = _version.get_versions()["version"]


def methods(
    output_dir: str | Path = Path("."),
    model_name: str | None = None,
    qc_only: bool = False,
) -> Path:
    """Write method section.

    :param output_dir: Defaults to Path(".")
    :type  output_dir: Union[str, Path], optional

    :param model_name: Defaults to None.
    :type  model_name: str, optional

    :return: Output file name.
    :rtype: Path
    """
    if isinstance(output_dir, str):
        output_dir = Path(output_dir)
    output_dir = output_dir.joinpath("logs")

    output_file = output_dir.joinpath("CITATION.md")
    create_dir_for_file(output_file)

    bib_file = str(Path(__file__).parent.joinpath("templates", "CITATION.bib"))
    shutil.copy(bib_file, output_dir)

    if not model_name:
        model_name = default_model()

    is_known_models = False
    is_default_model = False
    if model_name in available_models():
        is_known_models = True
        if model_name == default_model():
            is_default_model = True

    if not is_known_models:
        warnings.warn(f"{model_name} is not a known model name.")

    template_file = str(Path(__file__).parent.joinpath("templates", "CITATION.mustache"))
    with open(template_file) as template:

        output = chevron.render(
            template=template,
            data={
                "version": __version__,
                "model_name": model_name,
                "is_default_model": is_default_model,
                "is_known_models": is_known_models,
                "qc_only": qc_only,
            },
            warn=True,
        )

    output_file.write_text(output)

    return output_file
