from __future__ import annotations

import shutil
from pathlib import Path

from bidsmreye.methods import methods


def test_methods():

    ouptut_dir = Path.cwd().joinpath("temp")
    output_file = methods(ouptut_dir)

    assert output_file.is_file()

    shutil.rmtree(ouptut_dir)
