"""Write method section."""
import shutil
from pathlib import Path

import chevron

from bidsmreye.utils import create_dir_for_file


def methods(output_dir: Path = Path(".")):
    """Write method section."""

    output_dir = output_dir.joinpath("logs")
    output_file = output_dir.joinpath("CITATION.md")
    create_dir_for_file(output_file)

    bib_file = str(Path(__file__).parent.joinpath("templates", "CITATION.bib"))
    shutil.copy(bib_file, output_dir)

    template_file = str(Path(__file__).parent.joinpath("templates", "CITATION.mustache"))
    with open(template_file, "r") as template:

        foo = chevron.render(
            template=template,
            data={},
            warn=True,
        )

    output_file.write_text(foo)

    return output_file
