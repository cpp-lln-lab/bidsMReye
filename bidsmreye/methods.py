"""Write method section."""

from __future__ import annotations

import shutil
import warnings
from pathlib import Path

import chevron

from bidsmreye._version import __version__
from bidsmreye.defaults import available_models, default_model
from bidsmreye.utils import create_dir_for_file


def methods(
    output_dir: str | Path | None = None,
    model: str | None = None,
    qc_only: bool = False,
) -> Path:
    """Write method section.

    :param output_dir: Defaults to Path(".")
    :type  output_dir: Union[str, Path], optional

    :param model: Defaults to None.
    :type  model: str, optional

    :return: Output file name.
    :rtype: Path
    """
    if output_dir is None:
        output_dir = Path(".")
    if isinstance(output_dir, str):
        output_dir = Path(output_dir)
    output_dir = output_dir / "logs"

    output_file = output_dir / "CITATION.md"
    create_dir_for_file(output_file)

    bib_file = str(Path(__file__).parent / "templates" / "CITATION.bib")
    shutil.copy(bib_file, output_dir)

    if not model:
        model = default_model()

    is_known_models = False
    is_default_model = False
    if model in available_models():
        is_known_models = True
        if model == default_model():
            is_default_model = True

    if not is_known_models:
        warnings.warn(f"{model} is not a known model name.", stacklevel=3)

    template_file = str(Path(__file__).parent / "templates" / "CITATION.mustache")
    with open(template_file) as template:
        output = chevron.render(
            template=template,
            data={
                "version": __version__,
                "model": model,
                "is_default_model": is_default_model,
                "is_known_models": is_known_models,
                "qc_only": qc_only,
            },
            warn=True,
        )

    output_file.write_text(output)

    return output_file
