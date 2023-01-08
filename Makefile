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

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist


## PRE-TRAINED MODELS
.PHONY: models

clean-models: ## remove pretrained models
	rm -fr models/

models: ## gets all pretrained models from OSF
	bidsmreye_model --model_name all
models/dataset1_guided_fixations.h5:
	bidsmreye_model
models/dataset2_pursuit.h5:
	bidsmreye_model --model_name 2_pursuit
models/dataset3_openclosed.h5:
	bidsmreye_model --model_name 3_openclosed
models/dataset3_pursuit.h5:
	bidsmreye_model --model_name 3_pursuit
models/dataset4_pursuit.h5:
	bidsmreye_model --model_name 4_pursuit
models/dataset5_free_viewing.h5:
	bidsmreye_model --model_name 5_free_viewing


## STYLE

lint/flake8: ## check style with flake8
	flake8 bidsmreye tests
lint/black: ## check style with black
	black bidsmreye tests
lint/mypy: ## check style with mypy
	mypy bidsmreye

lint: lint/black lint/mypy lint/flake8  ## check style

validate_cff: ## Validate the citation file
	cffconvert --validate


## DOC
.PHONY: docs

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/source/bidsmreye.rst
	rm -f docs/source/modules.rst
	faqtory build
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
				--action prepare \
				-vv \
				--debug \
				--reset_database \
				--non_linear_coreg

generalize: ## demo: predicts labels of MOAE dataset
	bidsmreye 	$$PWD/tests/data/moae_fmriprep \
				$$PWD/outputs/moae_fmriprep/derivatives \
				participant \
				--action generalize \
				-vv \
				--debug \
				--reset_database \
				--non_linear_coreg


## Openneuro data
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
				--action prepare \
				--debug \
				--participant_label 302 307 \
				--space MNI152NLin2009cAsym \
				--run 1 2


ds002799_generalize:
	bidsmreye 	$$PWD/tests/data/ds002799/derivatives/fmriprep \
				$$PWD/outputs/ds002799/derivatives \
				participant \
				--action generalize \
				--debug \
				--participant_label 302 307 \
				--space MNI152NLin2009cAsym \
				--run 1 2


ds002799: clean-ds002799 get_ds002799
	bidsmreye	$$PWD/tests/data/ds002799/derivatives/fmriprep \
				$$PWD/outputs/ds002799/derivatives \
				participant \
				--action all \
				--debug \
				--participant_label 302 307 \
				--space MNI152NLin2009cAsym \
				--run 1 2 \
				-vv

## DOCKER
.PHONY: Dockerfile Dockerfile

Dockerfile: ## Dockerfile for the bidsmreye docker image using local package
	docker run --rm kaczmarj/neurodocker:0.9.1 generate docker \
	--base-image ubuntu:jammy \
	--pkg-manager apt \
	--install "git wget make" \
	--run "mkdir -p /home/neuro/bidsMReye/models" \
	--workdir /home/neuro/bidsMReye \
	--run "wget -q https://osf.io/download/cqf74/ -O models/dataset1_guided_fixations.h5" \
	--run "wget -q https://osf.io/download/4f6m7/ -O models/dataset2_pursuit.h5" \
	--run "wget -q https://osf.io/download/8cr2j/ -O models/dataset3_openclosed.h5" \
	--run "wget -q https://osf.io/download/e89wp/ -O models/dataset3_pursuit.h5" \
	--run "wget -q https://osf.io/download/96nyp/ -O models/dataset4_pursuit.h5" \
	--run "wget -q https://osf.io/download/89nky/ -O models/dataset5_free_viewing.h5" \
	--run "wget -q https://osf.io/download/23t5v/ -O models/dataset_1to5.h5" \
	--run "wget -q https://osf.io/download/mr87v/ -O models/dataset_1to6.h5" \
	--copy . /home/neuro/bidsMReye \
	--miniconda \
		conda_install="python=3.10 pip" \
		version="latest" \
		pip_install="-e ." \
	--copy ./docker/entrypoint.sh /neurodocker/startup.sh \
	--run "chmod +x /neurodocker/startup.sh" > Dockerfile

docker_build: Dockerfile
	docker build --tag cpplab/bidsmreye:unstable --file Dockerfile .

docker_build_no_cache: Dockerfile
	docker build --tag cpplab/bidsmreye:unstable --no-cache --file Dockerfile .

docker_demo: docker_build clean-demo
	make docker_prepare_data
	make docker_generalize

docker_prepare_data:
	docker run --rm -it \
				--user "$$(id -u):$$(id -g)" \
				-v $$PWD/tests/data/moae_fmriprep:/home/neuro/data \
				-v $$PWD/outputs/moae_fmriprep/derivatives:/home/neuro/outputs/ \
				cpplab/bidsmreye:unstable \
				/home/neuro/data/ \
				/home/neuro/outputs/ \
				participant \
				--action prepare \
				--debug \
				--reset_database

docker_generalize:
	docker run --rm -it \
				--user "$$(id -u):$$(id -g)" \
				-v $$PWD/tests/data/moae_fmriprep:/home/neuro/data \
				-v $$PWD/outputs/moae_fmriprep/derivatives:/home/neuro/outputs/ \
				cpplab/bidsmreye:unstable \
				/home/neuro/data/ \
				/home/neuro/outputs/ \
				participant \
				--action generalize
