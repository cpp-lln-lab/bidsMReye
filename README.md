[![Test demo](https://github.com/cpp-lln-lab/bidsMReye/actions/workflows/test_demo.yml/badge.svg)](https://github.com/cpp-lln-lab/bidsMReye/actions/workflows/test_demo.yml)
[![Test and coverage](https://github.com/cpp-lln-lab/bidsMReye/actions/workflows/test_and_coverage.yml/badge.svg)](https://github.com/cpp-lln-lab/bidsMReye/actions/workflows/test_and_coverage.yml)
[![Documentation Status](https://readthedocs.org/projects/bidsmreye/badge/?version=latest)](https://bidsmreye.readthedocs.io/en/latest/?badge=latest)
![https://github.com/psf/black](https://img.shields.io/badge/code%20style-black-000000.svg)

# bidsMReye

- [bidsMReye](#bidsmreye) - [Install](#install) - [dev install](#dev-install) -
  [Demo](#demo) - [Example](#example) - [Credits](#credits)

BIDS app using deepMReye to decode eye motion for fMRI time series data.

To be used on preprocessed BIDS derivatives (like those from fMRIprep), to
predict eye movements from the bold data when no eye movement data are
available.

UBy default it uses the deepMReye pre-trained "fixation" model.

The first part of the pipeline can however be used to extract data, irrespective
of the presence of eye movement labels and could thus be usefull to share
anonimysed subject data to the deepMReye dev team to allow them to improve their
pre-trained models.

- Free software: GNU General Public License v3
- Documentation: https://bidsmreye.readthedocs.io.

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
