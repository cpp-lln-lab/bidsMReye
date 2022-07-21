"""foo."""
from deepmreye import preprocess
from rich import print

from bidsmreye.bidsutils import check_layout
from bidsmreye.bidsutils import create_bidsname
from bidsmreye.bidsutils import get_dataset_layout
from bidsmreye.bidsutils import set_dataset_description
from bidsmreye.bidsutils import write_dataset_description
from bidsmreye.utils import create_dir_if_absent
from bidsmreye.utils import get_deepmreye_filename
from bidsmreye.utils import list_subjects
from bidsmreye.utils import move_file
from bidsmreye.utils import return_regex


def coregister_and_extract_data(img: str):
    """_summary_.

    Args:
        img (str): _description_
    """
    (
        eyemask_small,
        eyemask_big,
        dme_template,
        mask,
        x_edges,
        y_edges,
        z_edges,
    ) = preprocess.get_masks()

    print(f"Input file: {img}")

    preprocess.run_participant(
        img, dme_template, eyemask_big, eyemask_small, x_edges, y_edges, z_edges
    )


def preprocess_subject(cfg, layout_in, layout_out, subject_label: str):
    """Run coregistration and extract data for one subject.

    Args:
        layout_in (_type_): _description_
        subject_label (str): Can be a regular expression.
    """
    print(f"Running subject: {subject_label}")

    bf = layout_in.get(
        return_type="filename",
        subject=return_regex(subject_label),
        suffix="^bold$",
        task=return_regex(cfg["task"]),
        space=return_regex(cfg["space"]),
        extension=".nii.*",
        regex_search=True,
    )

    for img in bf:
        coregister_and_extract_data(img)

        mask_name = create_bidsname(layout_out, img, "mask")
        deepmreye_mask_name = get_deepmreye_filename(layout_in, img, "mask")
        move_file(deepmreye_mask_name, mask_name)

        report_name = create_bidsname(layout_out, img, "report")
        deepmreye_mask_report = get_deepmreye_filename(layout_in, img, "report")
        move_file(deepmreye_mask_report, report_name)


def prepare_data(cfg):
    """Run coregistration and extract data for all subjects.

    Args:
        dataset_path (_type_): _description_
    """
    input_dataset_path = cfg["input_folder"]
    print(f"\nindexing {input_dataset_path}\n")

    layout_in = get_dataset_layout(input_dataset_path)
    check_layout(layout_in)

    create_dir_if_absent(cfg["output_folder"])
    layout_out = get_dataset_layout(cfg["output_folder"])
    layout_out = set_dataset_description(layout_out)
    layout_out.dataset_description["DatasetType"] = "derivative"
    layout_out.dataset_description["GeneratedBy"][0]["Name"] = "bidsmreye"
    write_dataset_description(layout_out)

    subjects = list_subjects(layout_in, cfg)
    if cfg["debug"]:
        subjects = [subjects[0]]

    print(f"processing subjects: {subjects}\n")

    for subject_label in subjects:

        preprocess_subject(cfg, layout_in, layout_out, subject_label)
