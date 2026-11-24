"""Write method section."""

import shutil
import warnings
from pathlib import Path

from bidsmreye._version import __version__
from bidsmreye.defaults import available_models, default_model
from bidsmreye.report import TEMPLATES_DIR, return_jinja_env
from bidsmreye.utils import create_dir_for_file


def _model_name(model: str | Path) -> str:
    """Return the name of a pre-trained model from the path to its weights.

    Other model files are returned by their file name.
    """
    if isinstance(model, str) and model in available_models():
        return model
    stem = Path(model).stem
    if stem.startswith("dataset_") and stem[len("dataset_") :] in available_models():
        return stem[len("dataset_") :]
    return Path(model).name


def methods(
    output_dir: str | Path | None = None,
    model: str | Path | None = None,
    qc_only: bool = False,
) -> Path:
    """Write method section.

    :param output_dir: Defaults to Path(".")
    :type  output_dir: Union[str, Path], optional

    :param model: Name of a pre-trained model or path to a model file.
                  Defaults to None.
    :type  model: str | Path, optional

    :return: Output file name.
    :rtype: Path
    """
    if output_dir is None:
        output_dir = Path()
    if isinstance(output_dir, str):
        output_dir = Path(output_dir)
    output_dir = output_dir / "logs"

    output_file = output_dir / "CITATION.md"
    create_dir_for_file(output_file)

    bib_file = str(Path(__file__).parent / "templates" / "CITATION.bib")
    shutil.copy(bib_file, output_dir)

    if not model:
        model = default_model()
    is_model_file = isinstance(model, Path) or bool(Path(model).suffix)
    model = _model_name(model)

    is_known_model = False
    is_default_model = False
    if model in available_models():
        is_known_model = True
        if model == default_model():
            is_default_model = True

    if not is_known_model and not is_model_file:
        warnings.warn(f"{model} is not a known model name.", stacklevel=3)

    env = return_jinja_env(searchpath=TEMPLATES_DIR)
    template = env.get_template("CITATION.jinja")

    output = template.render(
        version=__version__,
        model=model,
        is_default_model=is_default_model,
        is_known_model=is_known_model,
        qc_only=qc_only,
    )

    output_file.write_text(output)

    return output_file
