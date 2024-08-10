"""Compile outputs from all tasks, spaces, runs into a single HTML."""

import datetime
from collections.abc import Iterable
from os import PathLike
from pathlib import Path
from typing import Union

from jinja2 import Environment, FileSystemLoader, select_autoescape

from bidsmreye._version import __version__
from bidsmreye.logger import bidsmreye_log

log = bidsmreye_log(name="bidsmreye")

TEMPLATES_DIR = Path(__file__).parent / "templates"

SearchpathType = Union[str | PathLike[str] | Iterable[str | PathLike[str]]]


def return_jinja_env(searchpath: Union[SearchpathType, None] = None) -> Environment:
    if searchpath is None:
        searchpath = TEMPLATES_DIR / "report"
    return Environment(
        loader=FileSystemLoader(searchpath),
        autoescape=select_autoescape(),
        lstrip_blocks=True,
        trim_blocks=True,
    )


def generate_report(output_dir: Path, subject_label: str, action: str) -> None:

    env = return_jinja_env()
    template = env.get_template("base.html")

    if action == "prepare":
        input_files = sorted(output_dir.glob(f"sub-{subject_label}/**/*report.html"))
    elif action == "generalize":
        input_files = sorted(output_dir.glob(f"sub-{subject_label}/**/*eyetrack.html"))

    files = []
    for html_report in input_files:
        with open(html_report) as f:
            content = f.read()

        name: str = html_report.stem
        if action == "prepare":
            name = name.replace("_desc-eye_report", "_desc-preproc_bold")

        files.append({"name": name, "content": content, "path": html_report})

    date = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()

    report = template.render(
        action=action,
        files=files,
        subject_label=subject_label,
        date=date,
        version=__version__,
    )

    report_filename = (
        output_dir / f"sub-{subject_label}" / f"sub-{subject_label}_{action}.html"
    )

    with open(report_filename, "w") as f:
        f.write(report)

    log.info(f"Report saved at: '{report_filename}'.")


if __name__ == "__main__":

    cwd = Path("/home/remi/github/cpp-lln-lab/bidsMReye")

    output_dir = cwd / "outputs" / "moae_fmriprep" / "derivatives" / "bidsmreye"
    subject = "01"

    output_dir = Path("/home/remi/gin/CPP/yin/bidsmreye")
    subject_label = "02"

    action = "prepare"

    generate_report(output_dir, subject_label, action)
