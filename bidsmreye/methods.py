"""Write method section."""
from __future__ import annotations

import shutil
from pathlib import Path

import chevron

from . import _version
from bidsmreye.utils import create_dir_for_file

__version__ = _version.get_versions()["version"]


def methods(output_dir: str | Path = Path(".")) -> Path:
    """Write method section.

    :param output_dir: Defaults to Path(".")
    :type  output_dir: Union[str, Path], optional

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

    template_file = str(Path(__file__).parent.joinpath("templates", "CITATION.mustache"))
    with open(template_file) as template:

        foo = chevron.render(
            template=template,
            data={"version": __version__},
            warn=True,
        )

    output_file.write_text(foo)

    return output_file
