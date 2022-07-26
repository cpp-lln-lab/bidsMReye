[![Test demo](https://github.com/cpp-lln-lab/bidsMReye/actions/workflows/test_demo.yml/badge.svg)](https://github.com/cpp-lln-lab/bidsMReye/actions/workflows/test_demo.yml)
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
[![Test and coverage](https://github.com/cpp-lln-lab/bidsMReye/actions/workflows/test_and_coverage.yml/badge.svg)](https://github.com/cpp-lln-lab/bidsMReye/actions/workflows/test_and_coverage.yml)
[![codecov](https://codecov.io/gh/cpp-lln-lab/bidsMReye/branch/main/graph/badge.svg?token=G5fm2kaloM)](https://codecov.io/gh/cpp-lln-lab/bidsMReye)
[![Documentation Status](https://readthedocs.org/projects/bidsmreye/badge/?version=latest)](https://bidsmreye.readthedocs.io/en/latest/?badge=latest)
![https://github.com/psf/black](https://img.shields.io/badge/code%20style-black-000000.svg)

# bidsMReye

BIDS app using [deepMReye](https://github.com/DeepMReye/DeepMReye) to decode eye
motion for fMRI time series data.

To be used on preprocessed BIDS derivatives (like those from fMRIprep), to
predict eye movements from the bold data when no eye movement data are
available.

By default it uses the [deepMReye](https://github.com/DeepMReye/DeepMReye)
[pre-trained "fixation" model](https://osf.io/cqf74).

The first part of the pipeline can however be used to extract data, irrespective
of the presence of eye movement labels and could thus be usefull to share
anonimysed subject data to the
[deepMReye](https://github.com/DeepMReye/DeepMReye) dev team to allow them to
improve their pre-trained models.

## Install

Clone this repository.

```bash
git clone git://github.com/cpp-lln-lab/bidsmreye
```

Then install it.

```bash
cd bidsMReye
pip install .
```

## Demo

For Linux or MacOS you use `make` to run all the different steps of the demo.

```bash
make demo
```

For Windows you will have to download the data and the pre-trained weights
manually.

- data
  - URL: [https://osf.io/vufjs/download](https://osf.io/vufjs/download)
  - destination folder: tests/data/moae_fmriprep

- model:
  - URL: [https://osf.io/download/cqf74/](https://osf.io/download/cqf74/)
  - destination file: models/dataset1_guided_fixations.h5

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

Running the different steps of the demo:

```bash
bids_dir="$PWD/tests/data/moae_fmriprep "
output_dir="$PWD/outputs "

bidsmreye --space MNI152NLin6Asym \
                --task auditory \
                --action prepare \
                $bids_dir \
                $output_dir

bidsmreye --space MNI152NLin6Asym \
                --task auditory \
                --action combine \
                $bids_dir \
                $output_dir

bidsmreye --space MNI152NLin6Asym \
                --task auditory \
                --action generalize \
                --model guided_fixations \
                $bids_dir \
                $output_dir
```

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://weexee.github.io/Portfolio/"><img src="https://avatars.githubusercontent.com/u/91776803?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Pauline Cabee</b></sub></a><br /><a href="https://github.com/cpp-lln-lab/bidsMReye/commits?author=WeeXee" title="Code">💻</a> <a href="#ideas-WeeXee" title="Ideas, Planning, & Feedback">🤔</a> <a href="#infra-WeeXee" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
