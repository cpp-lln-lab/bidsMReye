# bids app version of deepMReye

To be used on preprocessed BIDS derivatives (like those from fMRIprep), to
predict eye movements from the bold data when no eye movement data are
available.

Uses the deepMReye pre-trained "fixation" model.

The first part of the pipeline can however be used to extract data, irrespective
of the presence of eye movement labels and could thus be usefull to share
anomysed subject data to the deepMReye dev team to allow them to improve their
pre-trained models.

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

## dev install

use poetry

run poetry install

## Run

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
