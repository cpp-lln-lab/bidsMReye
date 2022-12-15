from __future__ import annotations

import shutil
from pathlib import Path

from bidsmreye.methods import methods


def test_methods():

    output_dir = Path.cwd().joinpath("temp")
    output_file = methods(output_dir)

    assert output_file.is_file()

    shutil.rmtree(output_dir)
