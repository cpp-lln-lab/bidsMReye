[![Test demo](https://github.com/cpp-lln-lab/bidsMReye/actions/workflows/test_demo.yml/badge.svg)](https://github.com/cpp-lln-lab/bidsMReye/actions/workflows/test_demo.yml)
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

Inside a virtual environment (`conda` or `virtualenv` or whatever floats your
boat ⛵)

```bash
virtualenv -p /usr/bin/python3.8 env
source env/bin/activate
```

```bash
pip install .
```

## dev install

```bash
pip install -r requirements_dev.txt
```

## Demo

Requires make

```
git clone https://github.com/cpp-lln-lab/bidsMReye.git
cd bidsMReye
pip install .
make demo
```

## Example

```bash
bids_dir="$PWD/tests/data/moae_fmriprep "
output_dir="$PWD/outputs "

python3 bidsmreye.py \
        --space MNI152NLin6Asym \
        --task auditory \
        --action prepare \
        $bids_dir \
        $output_dir

python3 bidsmreye.py \
        --space MNI152NLin6Asym \
        --task auditory \
        --action combine \
        $bids_dir \
        $output_dir

python3 bidsmreye.py \
        --space MNI152NLin6Asym \
        --task auditory \
        --action generalize \
        --model guided_fixations \
        $bids_dir \
        $output_dir

python3 bidsmreye.py \
        --space MNI152NLin6Asym \
        --task auditory \
        --action confounds \
        $bids_dir \
        $output_dir
```

## Credits

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
project template.
