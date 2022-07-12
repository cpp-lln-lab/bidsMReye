# bidsMReye

- Free software: GNU General Public License v3
- Documentation: https://bidsmreye.readthedocs.io.

<!--
.. image:: https://img.shields.io/pypi/v/bidsmreye.svg
        :target: https://pypi.python.org/pypi/bidsmreye

.. image:: https://img.shields.io/travis/Remi-Gau/bidsmreye.svg
        :target: https://travis-ci.com/Remi-Gau/bidsmreye

.. image:: https://readthedocs.org/projects/bidsmreye/badge/?version=latest
        :target: https://bidsmreye.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/Remi-Gau/bidsmreye/shield.svg
     :target: https://pyup.io/repos/github/Remi-Gau/bidsmreye/
     :alt: Updates
-->

BIDS app using deepMReye to decode eye motion for fMRI time series data

To be used on preprocessed BIDS derivatives (like those from fMRIprep), to
predict eye movements from the bold data when no eye movement data are
available.

Uses the deepMReye pre-trained "fixation" model.

The first part of the pipeline can however be used to extract data, irrespective
of the presence of eye movement labels and could thus be usefull to share
anonimysed subject data to the deepMReye dev team to allow them to improve their
pre-trained models.

- [bidsMReye](#bidsmreye) - [Install](#install) - [dev install](#dev-install) -
  [Demo](#demo) - [Run](#run) - [Credits](#credits)

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
pip install -r requirements.txt
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

input_dataset="/home/remi/gin/CPP/can_blind_restingState/derivatives/fmriprep"
output_location="/home/remi/gin/CPP/can_blind_restingState/derivatives/bidsmreye"

python bidsmreye.py
              --participant-label cb01 \
              --action prepare \
              --dry-run true
              ${input_dataset} \
              ${output_location} \
              participant
```

At the moment several value, including the input dataset, are hard coded in
`utils.config`.

```bash
bids_dir="$PWD/tests/data/moae_fmriprep"
output_dir="$PWD/outputs"
python3 bidsmreye.py $bids_dir $output_dir participant --action prepare
```

```bash
python3 combine.py
```

```bash
python3 generalize.py
```

```bash
python3 generate_confounds.py
```

## Credits

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
project template.
