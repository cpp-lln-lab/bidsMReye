---
title: "How I should structure my input data?"
alt_titles:
  - bidsmreye gives me an error saying that the dataset must in bids format.
  - "What input format does bidsmreye expect?"
---

bidsmreye requires a BIDS **preprocessed** dataset as input.

Two bids apps are available to generate those types of preprocessed data:

- [fmriprep](https://fmriprep.org/en/stable/)
- [bidspm](https://bidspm.readthedocs.io/en/latest/general_information.html)

bidsmreye requires your input fmri data:

 - to be minimally preprocessed
 - with [filenames and structure that conforms to a BIDS derivative dataset](https://bids-specification.readthedocs.io/en/latest/derivatives/imaging.html#preprocessed-coregistered-andor-resampled-volumes).

More specifically the dataset should look like this:

```
dataset_description.json
sub-{sub}
    [ses-{session}]
        func (func_dir)
            sub-{sub}[_ses-{session}]_task-{task}[_acq-{acq}][_ce-{ce}][_dir-{dir}][_rec-{rec}][_run-{run_index}]_space-{space}[_res-{res}]_desc-preproc_bold.nii[.gz]
[participants.tsv]
[README]
[CHANGES]
[LICENSE]
```

- Filename entities, files or directories between square brackets
  (for example, `[_ses-<label>]`) are OPTIONAL.
  Note that for bidsmreye to work, the `space` entity is required.
- `[.gz]` means that both the unzipped and gzipped versions of the extension are valid.

Moreover the dataset_description.json file specify
that the input dataset is a derivative dataset:

```json
{
    "Name": "my_dataset",
    "BIDSVersion": "1.8.0",
    "DatasetType": "derivative",
}
```
