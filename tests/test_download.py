from __future__ import annotations

from bidsmreye.download import download_parser


def test_download_parser():
    """Test parser."""
    parser = download_parser()
    assert parser.description == "Download deepmreye pretrained model from OSF."

    args, unknowns = parser.parse_known_args(
        [
            "--model_name",
            "1_guided_fixations",
            "--output_dir",
            "/home/bob/models",
        ]
    )

    assert args.output_dir == "/home/bob/models"
