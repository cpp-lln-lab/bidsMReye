# Demo

This deom will run the docker image of bidsMReye
on the fmriprep preprocessed data of the SPM MOAE dataset
(that you can find on the open science framework).

For Linux or MacOS you can use `make` to get the data of the demo.

```bash
make tests/data/moae_fmriprep
```

For Windows you will have to download the data manually.

- data

  - URL: [https://osf.io/vufjs/download](https://osf.io/vufjs/download)
  - destination folder: `tests/data/moae_fmriprep`

The directory where you want to run the demo should look like this:

```bash
└── tests
    └── data
        └── moae_fmriprep
             ├── logs
             └── sub-01
                 ├── anat
                 ├── figures
                 └── func
```

## Preparing the data

Extracts the timeseries from the eye mask in the preprocessed fMRI images.

```bash
docker run --rm -it \
      --user "$(id -u):$(id -g)" \
      -v $PWD/tests/data/moae_fmriprep:/home/neuro/data \
      -v $PWD/outputs/moae_fmriprep/derivatives:/home/neuro/outputs/ \
            cpplab/bidsmreye:latest \
            /home/neuro/data/ \
            /home/neuro/outputs/ \
            participant \
            prepare
```

## Computing the eye movements

This step will use the extracted timeseries to predict the eye movements
using the default pre-trained model of deepmreye.

```bash
docker run --rm -it \
      --user "$(id -u):$(id -g)" \
      -v $PWD/tests/data/moae_fmriprep:/home/neuro/data \
      -v $PWD/outputs/moae_fmriprep/derivatives:/home/neuro/outputs/ \
            cpplab/bidsmreye:latest \
            /home/neuro/data/ \
            /home/neuro/outputs/ \
            participant \
            generalize
```
