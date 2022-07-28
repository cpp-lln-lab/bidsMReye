# Demo

This will run bidsMReye on the fmriprep preprocessed data of the SPM MOAE
dataset (that you can find on the open science framework).

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
├── models
│   └── dataset1_guided_fixations.h5
└── tests
    └── data
        └── moae_fmriprep
             ├── logs
             └── sub-01
                 ├── anat
                 ├── figures
                 └── func
```

## Using docker

For Linux or MacOS you can use `make` to get run all the steps of the demo.

```bash
make docker_demo
```

This will run the different steps of the demo:

```bash
docker run --rm -it \
      --user "$(id -u):$(id -g)" \
      -v $PWD/tests/data/moae_fmriprep:/home/neuro/data \
      -v $PWD/outputs:/home/neuro/outputs \
      bidsmreye:latest \
      /home/neuro/data/ \
      /home/neuro/outputs/ \
      participant \
      --action prepare


docker run --rm -it \
      --user "$(id -u):$(id -g)" \
      -v $PWD/tests/data/moae_fmriprep:/home/neuro/data \
      -v $PWD/outputs:/home/neuro/outputs \
      bidsmreye:latest \
      /home/neuro/data/ \
      /home/neuro/outputs/ \
      participant \
      --action combine


docker run --rm -it \
      --user "$(id -u):$(id -g)" \
      -v $PWD/tests/data/moae_fmriprep:/home/neuro/data \
      -v $PWD/outputs:/home/neuro/outputs \
      bidsmreye:latest \
      /home/neuro/data/ \
      /home/neuro/outputs/ \
      participant \
      --action generalize
```

## After installing the package locally

For Linux or MacOS you can use `make` to get run all the steps of the demo.

```bash
make demo
```

This will run the different steps of the demo:

```bash
bids_dir="$PWD/tests/data/moae_fmriprep "
output_dir="$PWD/outputs "

bidsmreye --action prepare \
          $bids_dir \
          $output_dir

bidsmreye --action combine \
          $bids_dir \
          $output_dir

bidsmreye --action generalize \
          $bids_dir \
          $output_dir
```
