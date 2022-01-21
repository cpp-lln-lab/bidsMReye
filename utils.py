import os
import re
from os.path import abspath
from os.path import dirname
from os.path import join
from pathlib import Path

from bids import BIDSLayout
from rich import print


def config() -> dict:

    cfg = {
        "output_folder": "../outputs/deepMReye/",
        "input_folder": "../inputs/rest_blnd_can_fmriprep/",
        "model_weights_file": "../inputs/models/dataset1_guided_fixations.h5",
        "participant": [],
        "space": "MNI152NLin2009cAsym",
        "suffix": "bold",
        "task": "rest",
        "debug": False,
    }

    has_GPU = False

    os.environ["CUDA_VISIBLE_DEVICES"] = "0" if has_GPU else ""

    return cfg


def move_file(input: str, output: str):

    print(f"{abspath(input)} --> {abspath(output)}")
    create_dir_for_file(output)
    os.rename(input, output)


def create_dir_if_absent(output_path: str):
    if not Path(output_path).exists():
        print(f"Creating dir: {output_path}")
        os.makedirs(output_path)


def create_dir_for_file(file: str):
    output_path = dirname(abspath(file))
    create_dir_if_absent(output_path)


def return_regex(string):
    return f"^{string}$"


def list_subjects(layout, cfg={}):

    if cfg == {} or cfg["participant"] == []:
        subjects = layout.get_subjects()
    else:
        subjects = layout.get(
            return_type="id", target="subject", subject=cfg["participant"]
        )

    if subjects == [] or subjects is None:
        raise Exception("No subject found")

    return subjects


def get_dataset_layout(dataset_path: str):

    create_dir_if_absent(dataset_path)

    layout = BIDSLayout(dataset_path, validate=False, derivatives=False)
    return layout


def check_layout(layout):

    desc = layout.get_dataset_description()
    if desc["DatasetType"] != "derivative":
        raise Exception("Input dataset should be BIDS derivative")

    cfg = config()

    bf = layout.get(
        return_type="filename",
        task=cfg["task"],
        space=cfg["space"],
        suffix="^bold$",
        extension="nii.*",
        regex_search=True,
    )

    generated_by = desc["GeneratedBy"][0]["Name"]
    if generated_by.lower() == "deepmreye":
        bf = layout.get(
            return_type="filename",
            task=cfg["task"],
            space=cfg["space"],
            suffix="^mask$",
            extension="p",
            regex_search=True,
        )

    if bf == []:
        raise Exception("Input dataset does not have any data to process")


def return_path_rel_dataset(file_path: str, dataset_path: str) -> str:
    """
    Create file path relative to the root of a dataset
    """
    file_path = abspath(file_path)
    dataset_path = abspath(dataset_path)
    rel_path = file_path.replace(dataset_path, "")
    rel_path = rel_path[1:]
    return rel_path


def get_deepmreye_filename(layout, img: str, filetype: str) -> str:

    if isinstance(img, (list)):
        img = img[0]

    bf = layout.get_file(img)
    filename = bf.filename

    filename = return_deepmreye_output_filename(filename, filetype)

    filefolder = dirname(abspath(img))

    deepmreye_filename = join(filefolder, filename)

    return deepmreye_filename


def return_deepmreye_output_filename(filename: str, filetype: str) -> str:

    if filetype == "mask":
        filename = "mask_" + re.sub(r"\.nii.*", ".p", filename)
    elif filetype == "report":
        filename = "report_" + re.sub(r"\.nii.*", ".html", filename)

    return filename
