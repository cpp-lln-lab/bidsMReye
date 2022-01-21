from utils import config
from utils import get_dataset_layout
from utils import get_deepmreye_filename
from utils import list_subjects
from utils import return_deepmreye_output_filename
from utils import return_path_rel_dataset


def test_list_subjects():

    cfg = config()
    cfg["participant"] = ["sccb01"]

    layout = get_dataset_layout(cfg["input_folder"])

    subjects = list_subjects(layout, cfg)

    assert subjects == ["sccb01"]


def test_get_dataset_layout_smoke_test():
    get_dataset_layout("data")


def test_return_path_rel_dataset():

    file_path = "/home/john/gin/datset/sub-03/func/sub-03_task-rest_space-T1w_desc-preproc_bold.nii.gz"
    dataset_path = "/home/john/gin/datset"
    rel_file_path = return_path_rel_dataset(file_path, dataset_path)

    assert (
        rel_file_path
        == "sub-03/func/sub-03_task-rest_space-T1w_desc-preproc_bold.nii.gz"
    )


def test_get_deepmreye_filename():

    # TODO need dummy dataset to test this

    cfg = config()
    layout = get_dataset_layout(cfg["input_folder"])

    output_file = "/home/remi/github/CPP_deepMReye/inputs/rest_blnd_can_fmriprep/sub-cb01/func/mask_sub-cb01_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.p"

    img = layout.get(
        return_type="filename",
        subject="cb01",
        suffix="bold",
        task="rest",
        space="MNI152NLin2009cAsym",
        extension=".nii.gz",
    )
    deepmreye_mask_name = get_deepmreye_filename(layout, img, "mask")

    assert deepmreye_mask_name == output_file


def test_return_deepmreye_output_filename():

    input_file = "sub-01_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"
    output_filename = return_deepmreye_output_filename(input_file, "mask")
    expected_output_file = (
        "mask_sub-01_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.p"
    )
    assert output_filename == expected_output_file

    input_file = "sub-01_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii"
    output_filename = return_deepmreye_output_filename(input_file, "mask")
    assert output_filename == expected_output_file
