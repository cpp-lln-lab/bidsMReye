from __future__ import annotations

import shutil
from pathlib import Path

from bidsmreye.methods import methods


def test_methods():

    output_dir = Path.cwd().joinpath("temp")
    output_file = methods(output_dir=output_dir)

    assert output_dir.is_dir()
    assert output_file.is_file()

    shutil.rmtree(output_dir)


def test_methods_calibration_data():

    output_dir = Path.cwd().joinpath("temp")
    output_file = methods(output_dir=output_dir, model_name="calibration_data")

    assert output_dir.is_dir()
    assert output_file.is_file()

    shutil.rmtree(output_dir)


def test_methods_qc_only():

    output_dir = Path.cwd().joinpath("temp")
    output_file = methods(output_dir=output_dir, qc_only=True)

    assert output_dir.is_dir()
    assert output_file.is_file()

    shutil.rmtree(output_dir)
