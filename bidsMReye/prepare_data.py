from bidsname import create_bidsname
from bidsname import set_dataset_description
from bidsname import write_dataset_description
from deepmreye import preprocess
from rich import print
from utils import check_layout
from utils import config
from utils import create_dir_if_absent
from utils import get_dataset_layout
from utils import get_deepmreye_filename
from utils import list_subjects
from utils import move_file
from utils import return_regex


def coregister_and_extract_data(img: str):

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


def preprocess_subject(layout, subject_label):

    cfg = config()

    # TODO performance: do not reload the input layout for every subject
    layout = get_dataset_layout(cfg["input_folder"])

    print(f"Running subject: {subject_label}")

    bf = layout.get(
        return_type="filename",
        subject=return_regex(subject_label),
        suffix="^bold$",
        task=return_regex(cfg["task"]),
        space=return_regex(cfg["space"]),
        extension=".nii.*",
        regex_search=True,
    )

    # TODO performance: do not reload the output layout for every subject
    output = get_dataset_layout(cfg["output_folder"])

    for img in bf:
        coregister_and_extract_data(img)

        mask_name = create_bidsname(output, img, "mask")
        deepmreye_mask_name = get_deepmreye_filename(layout, img, "mask")
        move_file(deepmreye_mask_name, mask_name)

        report_name = create_bidsname(output, img, "report")
        deepmreye_mask_report = get_deepmreye_filename(layout, img, "report")
        move_file(deepmreye_mask_report, report_name)


def preprocess_dataset(dataset_path):

    cfg = config()

    layout = get_dataset_layout(dataset_path)
    check_layout(layout)

    create_dir_if_absent(cfg["output_folder"])
    output = get_dataset_layout(cfg["output_folder"])
    output = set_dataset_description(output)
    output.dataset_description["DatasetType"] = "derivative"
    output.dataset_description["GeneratedBy"][0]["Name"] = "deepMReye"
    write_dataset_description(output)

    subjects = list_subjects(layout, cfg)
    if cfg["debug"]:
        subjects = [subjects[0]]

    print(f"processing subjects: {subjects}\n")

    for subject_label in subjects:

        preprocess_subject(layout, subject_label)


def main():

    cfg = config()

    print(f"\nindexing {cfg['input_folder']}\n")
    preprocess_dataset(cfg["input_folder"])


if __name__ == "__main__":

    main()
