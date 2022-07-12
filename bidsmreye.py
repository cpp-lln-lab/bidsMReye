"""foo."""
import argparse
import os
from glob import glob

from rich import print

from bidsmreye.combine import combine
from bidsmreye.generalize import generalize
from bidsmreye.generate_confounds import generate_confounds
from bidsmreye.prepare_data import prepare_data
from bidsmreye.utils import config


parser = argparse.ArgumentParser(description="Example BIDS App entrypoint script.")
parser.add_argument(
    "bids_dir",
    help="The directory with the input dataset "
    "formatted according to the BIDS standard.",
)
parser.add_argument(
    "output_dir",
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
    choices=["participant"],
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
    "--action",
    help="what to do",
    choices=["prepare", "combine", "generalize", "confounds"],
)
parser.add_argument(
    "--task",
    help="task to process",
)
parser.add_argument(
    "--space",
    help="space to process",
)
parser.add_argument(
    "--model",
    help="model to use",
    choices=["guided_fixations"],
)
parser.add_argument(
    "--debug",
    help="true or false",
)

args = parser.parse_args()

subjects_to_analyze = []
# only for a subset of subjects
if args.participant_label:
    subjects_to_analyze = args.participant_label
# for all subjects
else:
    subject_dirs = glob(os.path.join(args.bids_dir, "sub-*"))
    subjects_to_analyze = [subject_dir.split("-")[-1] for subject_dir in subject_dirs]

cfg = config()

if args.task:
    cfg["task"] = args.task
if args.task:
    cfg["space"] = args.space

cfg["input_folder"] = args.bids_dir
cfg["output_folder"] = os.path.join(args.output_dir, "bidsmreye")

if args.model == "guided_fixations":
    cfg["model_weights_file"] = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "models",
        "dataset1_guided_fixations.h5",
    )

print(cfg["model_weights_file"])

if args.analysis_level == "participant":

    if args.action == "prepare":
        prepare_data(cfg)

    elif args.action == "combine":
        combine(cfg)

    elif args.action == "generalize":
        generalize(cfg)

    elif args.action == "confounds":
        generate_confounds(cfg)
