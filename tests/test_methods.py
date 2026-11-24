import warnings

from bidsmreye.methods import methods


def test_methods(tmp_path):
    output_file = methods(output_dir=tmp_path)

    assert output_file.is_file()


def test_methods_calibration_data(tmp_path):
    output_file = methods(output_dir=tmp_path, model="calibration_data")
    assert output_file.is_file()


def test_methods_qc_only(tmp_path):
    output_file = methods(output_dir=tmp_path, qc_only=True)
    assert output_file.is_file()


def test_methods_pretrained_model_file(tmp_path):
    """The path to a downloaded pre-trained model is cited as that model."""
    output_file = methods(
        output_dir=tmp_path, model=tmp_path / "models" / "dataset_1to6.h5"
    )
    content = output_file.read_text()
    assert "pre-trained model 1to6" in content
    assert "This model was trained on" in content


def test_methods_model_file(tmp_path):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        output_file = methods(output_dir=tmp_path, model=str(tmp_path / "my_model.h5"))
    content = output_file.read_text()
    assert "pre-trained" not in content
    assert "`my_model.h5`" in content
