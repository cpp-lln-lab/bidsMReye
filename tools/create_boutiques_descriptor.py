import boutiques.creator as bc

from bidsmreye._parsers import common_parser

newDescriptor = bc.CreateDescriptor(common_parser(), execname="bidsmreye")

# newDescriptor.save("bidsmreye_0.4.0.json")

cmd = (
    "$PWD/tests/data/moae_fmriprep "
    "$PWD/outputs/moae_fmriprep/derivatives "
    "participant "
    "all "
    "--reset_database --non_linear_coreg --model 1_guided_fixations -vv"
)
cmd = cmd.split(" ")

print(cmd)

parser = common_parser()

args = parser.parse_args(cmd)
invoc = newDescriptor.createInvocation(args)

# Then, if you want to save them to a file...
# import json
# with open('my-inputs.json', 'w') as fhandle:
#     fhandle.write(json.dumps(invoc, indent=4))
