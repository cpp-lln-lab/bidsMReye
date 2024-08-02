from __future__ import annotations

from bidsmreye.methods import methods


def test_methods(tmp_path):
    output_file = methods(output_dir=tmp_path)

    assert output_file.is_file()


def test_methods_calibration_data(tmp_path):
    output_file = methods(output_dir=tmp_path, model_name="calibration_data")
    assert output_file.is_file()


def test_methods_qc_only(tmp_path):
    output_file = methods(output_dir=tmp_path, qc_only=True)
    assert output_file.is_file()
