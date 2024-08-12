.PHONY: clean clean-build clean-pyc clean-test coverage dist  help install
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

# Put it first so that "make" without argument is like "make help".
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test clean-models clean-demo clean-models ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache


## INSTALL

install_dev: clean ## install the package and development dependencies to the active Python's site-packages
	pip install -e .[dev]
	make models

dist: clean ## builds source and wheel package
	python -m build
	ls -l dist

release: dist ## package and upload a release
	twine upload dist/*


## PRE-TRAINED MODELS
.PHONY: models

clean-models: ## remove pretrained models
	rm -fr models/

models:
	bidsmreye_model --model 1to6
models/dataset1_guided_fixations.h5:
	bidsmreye_model
models/dataset2_pursuit.h5:
	bidsmreye_model --model 2_pursuit
models/dataset3_openclosed.h5:
	bidsmreye_model --model 3_openclosed
models/dataset3_pursuit.h5:
	bidsmreye_model --model 3_pursuit
models/dataset4_pursuit.h5:
	bidsmreye_model --model 4_pursuit
models/dataset5_free_viewing.h5:
	bidsmreye_model --model 5_free_viewing


## DOC
.PHONY: docs docs/source/FAQ.md

docs/source/FAQ.md:
	faqtory build

docs: docs/source/FAQ.md ## generate Sphinx HTML documentation, including API docs
	rm -f docs/source/bidsmreye.rst
	rm -f docs/source/modules.rst
	sphinx-apidoc -o docs/source bidsmreye
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .


## TESTS

test: tests/data/moae_fmriprep ## run tests quickly with the default Python
	python -m pytest

tests/data/moae_fmriprep: ## gets fmriprep preprocessed data of the SPM MOAE dataset from OSF
	mkdir -p tests/data
	wget -q https://osf.io/vufjs/download
	unzip download
	rm download
	mv moae_fmriprep tests/data/moae_fmriprep


## DEMO
.PHONY: clean-demo

clean-demo:
	rm -fr outputs/moae_fmriprep

demo: clean-demo prepare generalize## demo: runs all demo steps on MOAE dataset

prepare: tests/data/moae_fmriprep ## demo: prepares the data of MOAE dataset
	bidsmreye 	$$PWD/tests/data/moae_fmriprep \
				$$PWD/outputs/moae_fmriprep/derivatives \
				participant \
				prepare \
				-vv \
				--reset_database \
				--linear_coreg

generalize: ## demo: predicts labels of MOAE dataset
	bidsmreye 	$$PWD/tests/data/moae_fmriprep \
				$$PWD/outputs/moae_fmriprep/derivatives \
				participant \
				generalize \
				--model 1_guided_fixations \
				-vv
	bidsmreye 	$$PWD/tests/data/moae_fmriprep \
				$$PWD/outputs/moae_fmriprep/derivatives \
				participant \
				generalize \
				-vv

# run demo via boutiques
demo_boutiques: tests/data/moae_fmriprep
	bosh exec launch --no-container boutiques/bidsmreye_0.4.0.json boutiques/invocation.json

## ds002799
.PHONY: get_ds002799_dat

clean-ds002799:
	rm -fr outputs/ds002799/derivatives

tests/data/data_ds002799:
	datalad install -s ///openneuro/ds002799 tests/data/ds002799

get_ds002799: tests/data/data_ds002799
	cd tests/data/ds002799/derivatives/fmriprep && \
	datalad get sub-30[27]/ses-*/func/*run-*preproc*bold*

ds002799_prepare: get_ds002799
	bidsmreye 	$$PWD/tests/data/ds002799/derivatives/fmriprep \
				$$PWD/outputs/ds002799/derivatives \
				participant \
				prepare \
				--participant_label 302 307 \
				--space MNI152NLin2009cAsym \
				--reset_database \
				--run 1 2


ds002799_generalize:
	bidsmreye 	$$PWD/tests/data/ds002799/derivatives/fmriprep \
				$$PWD/outputs/ds002799/derivatives \
				participant \
				generalize \
				--participant_label 302 307 \
				--space MNI152NLin2009cAsym \
				--run 1 2


ds002799: clean-ds002799 get_ds002799
	bidsmreye	$$PWD/tests/data/ds002799/derivatives/fmriprep \
				$$PWD/outputs/ds002799/derivatives \
				participant \
				all \
				--participant_label 302 307 \
				--space MNI152NLin2009cAsym \
				--run 1 2 \
				--reset_database \
				-vv

## ds000114
get_ds000114:
	datalad install -s ///openneuro-derivatives/ds000114-fmriprep tests/data/ds000114-fmriprep
	cd tests/data/ds000114-fmriprep && datalad get sub-0[1-2]/ses-*/func/*MNI*desc-preproc*bold.nii.gz -J 12

ds000114_all: get_ds000114
	bidsmreye 	$$PWD/tests/data/ds000114-fmriprep \
				$$PWD/outputs/ds000114/derivatives \
				participant \
				all \
				--participant_label 01 02 \
				--space MNI152NLin2009cAsym \
				--task linebisection overtverbgeneration -vv --force

ds000114_prepare: get_ds000114
	bidsmreye 	$$PWD/tests/data/ds000114-fmriprep \
				$$PWD/outputs/ds000114/derivatives \
				participant \
				prepare \
				--participant_label 01 02 \
				--space MNI152NLin2009cAsym \
				--task linebisection -vv

ds000114_generalize:
	bidsmreye 	$$PWD/tests/data/ds000114-fmriprep \
				$$PWD/outputs/ds000114/derivatives \
				participant \
				generalize \
				--participant_label 01 02 \
				--space MNI152NLin2009cAsym

ds000114_qc:
	bidsmreye 	$$PWD/outputs/ds000114/derivatives/bidsmreye \
				$$PWD/outputs/ds000114/derivatives \
				group \
				qc \
				--participant_label 01 02 \
				--space MNI152NLin2009cAsym \
				-vvv

## DOCKER
.PHONY:

docker_build:
	docker build --tag cpplab/bidsmreye:unstable --file Dockerfile .

docker_build_no_cache:
	docker build --tag cpplab/bidsmreye:unstable --no-cache --file Dockerfile .

docker_demo: clean-demo
	make docker_prepare_data
	make docker_generalize

docker_prepare_data:
	docker run --rm -it \
				-v $$PWD/tests/data/moae_fmriprep:/home/neuro/data \
				-v $$PWD/outputs/moae_fmriprep/derivatives:/home/neuro/outputs/ \
				cpplab/bidsmreye:unstable \
				/home/neuro/data/ \
				/home/neuro/outputs/ \
				participant \
				prepare \
				--reset_database

docker_generalize:
	docker run --rm -it \
				-v $$PWD/tests/data/moae_fmriprep:/home/neuro/data \
				-v $$PWD/outputs/moae_fmriprep/derivatives:/home/neuro/outputs/ \
				cpplab/bidsmreye:unstable \
				/home/neuro/data/ \
				/home/neuro/outputs/ \
				participant \
				generalize --model 1_guided_fixations

docker_ds002799: get_ds002799
# datalad unlock $$PWD/tests/data/ds002799/derivatives/fmriprep/sub-30[27]/ses-*/func/*run-*preproc*bold*
	docker run --rm -it \
				-v $$PWD/tests/data/ds002799/derivatives/fmriprep:/home/neuro/data \
				-v $$PWD/outputs/ds002799/derivatives:/home/neuro/outputs/ \
				cpplab/bidsmreye:unstable \
				/home/neuro/data/ \
				/home/neuro/outputs/ \
				participant \
				all \
				--participant_label 302 307 \
				--space MNI152NLin2009cAsym \
				--run 1 2 \
				--reset_database \
				-vv
