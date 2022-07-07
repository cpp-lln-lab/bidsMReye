# bidsMReye

-   Free software: GNU General Public License v3
-   Documentation: https://bidsmreye.readthedocs.io.

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

- [bidsMReye](#bidsmreye)
        - [Install](#install)
        - [DEV install](#dev-install)
        - [Run](#run)
        - [Credits](#credits)

## Install

Inside a virtual environment (`conda` or `virtualenv` or whatever floats your
boat ⛵)

```
virtualenv -p /usr/bin/python3.8 env
source env/bin/activate
```

From the `code` directory

<!-- TODO fix bug in deepMReye that makes it impossible to find the masks -->

```
pip install -r requirements.txt
cd lib/deepMReye
pip install .
```

## DEV install

use poetry

run poetry install

## Run


```bash

input_dataset="/home/remi/gin/CPP/can_blind_restingState/derivatives/fmriprep"
output_location="/home/remi/gin/CPP/can_blind_restingState/derivatives/bidsmreye"

python run.py --input-datasets ${input_dataset} \
              --output-location ${output_location} \
              --analysis-level subject \
              --participant-label cb01 \
              --action prepare \
              --dry-run true
```



python run.py



At the moment several value, including the input dataset, are hard coded in
`utils.config`.

```bash
python3 prepare_data.py
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

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.
