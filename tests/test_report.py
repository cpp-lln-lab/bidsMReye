import pathlib

from bidsmreye.report import generate_report


def test_generate_report(tmp_path):

    output_dir = pathlib.Path() / "outputs"
    output_dir = tmp_path

    (output_dir / "sub-01").mkdir(parents=True)
    generate_report(output_dir=output_dir, subject_label="01", action="prepare")
    generate_report(output_dir=output_dir, subject_label="01", action="generalize")

    assert (output_dir / "sub-01" / "sub-01_prepare.html").exists()
    assert (output_dir / "sub-01" / "sub-01_generalize.html").exists()
