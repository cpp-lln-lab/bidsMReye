#!/usr/bin/env python3
"""Main module."""
import argparse
from os.path import abspath

from rich import print

from bidsmreye.bidsutils import check_layout
from bidsmreye.bidsutils import get_dataset_layout

# from bidsmreye.bidsutils import get_bids_filter_config

# from bidsmreye.bidsutils import init_derivatives_layout

parser = argparse.ArgumentParser(description="Example BIDS App entrypoint script.")
parser.add_argument(
    "input-datasets",
    help="The directory with the input dataset formatted according to the BIDS standard.",
)
parser.add_argument(
    "output_location",
    help="The directory where the output files "
    "should be stored. If you are running group level analysis "
    "this folder should be prepopulated with the results of the"
    "participant level analysis.",
)
parser.add_argument(
    "analysis_level",
    help="Level of the analysis that will be performed. "
    "Multiple participant level analyses can be run independently "
    "(in parallel) using the same output_dir.",
    choices=["participant", "group"],
)
parser.add_argument(
    "--participant_label",
    help="The label(s) of the participant(s) that should be analyzed. The label "
    "corresponds to sub-<participant_label> from the BIDS spec "
    '(so it does not include "sub-"). If this parameter is not '
    "provided all subjects should be analyzed. Multiple "
    "participants can be specified with a space separated list.",
    nargs="+",
)
parser.add_argument(
    "--skip_bids_validator",
    help="Whether or not to perform BIDS dataset validation",
    action="store_true",
)

# TODO
# parser.add_argument(
#     "-v",
#     "--version",
#     action="version",
#     version=f"BIDS-App example version {__version__}",
# )


def main(
    input_datasets,
    output_location,
    analysis_level,
    participant_label,
    action,
    bids_filter_file,
    dry_run,
):
    """_summary_.

    Args:
        input_datasets (_type_): _description_
        output_location (_type_): _description_
        analysis_level (_type_): _description_
        participant_label (_type_): _description_
        action (_type_): _description_
        bids_filter_file (_type_): _description_
        dry_run (_type_): _description_
    """
    input_datasets = abspath(input_datasets)
    print(f"Input dataset: {input_datasets}")

    output_location = abspath(output_location)
    print(f"Output location: {output_location}")

    # if bids_filter_file == "":
    #     bids_filter = get_bids_filter_config()
    # else:
    #     bids_filter = get_bids_filter_config(bids_filter_file)

    if action == "prepare":

        layout_in = get_dataset_layout(input_datasets)
        check_layout(layout_in)

        # layout_out = init_derivatives_layout(output_location)

        # print(layout.get_subjects())

        # print(layout.get_sessions())

        # TODO add loop for subjects

        # skullstrip(layout_in, layout_out, participant_label, bids_filter=bids_filter)

    # elif action == "combine":

    # layout_out = get_dataset_layout(output_location)

    # segment(layout_out, participant_label, bids_filter=bids_filter, dry_run=dry_run)


if __name__ == "__main__":
    main()
