import importlib

from bidsmreye._cli import cli

bidsmreye_module = importlib.import_module("bidsmreye.bidsmreye")


def test_cli_model_path(tmp_path, pybids_test_dataset, monkeypatch):
    """A model file passed on the CLI is used as is: nothing is downloaded.

    https://github.com/cpp-lln-lab/bidsMReye/issues/91
    """
    model_file = tmp_path / "my_model.h5"
    model_file.write_bytes(b"")
    output_dir = tmp_path / "output"

    # do not actually run generalize, only capture the config it would get
    captured = {}

    def fake_dispatch(analysis_level, action, cfg):
        captured["cfg"] = cfg

    monkeypatch.setattr(bidsmreye_module, "dispatch", fake_dispatch)

    cli(
        [
            "bidsmreye",
            str(pybids_test_dataset),
            str(output_dir),
            "participant",
            "generalize",
            "--model",
            str(model_file),
        ]
    )

    assert captured["cfg"].model_weights_file == model_file.absolute()
    # no model was downloaded
    assert not (output_dir / "bidsmreye" / "models").exists()
