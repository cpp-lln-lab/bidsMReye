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

clean: clean-build clean-pyc clean-test clean-models clean-demo ## remove all build, test, coverage and Python artifacts

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
	rm -fr tests/data

clean-models: ## remove pretrained models
	rm -fr models/


## INSTALL

install: clean models ## install the package to the active Python's site-packages
	pip install .

install_dev: clean models ## install the package and development dependencies to the active Python's site-packages
	pip install -e .[dev]

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist


## PRE-TRAINED MODELS
models: models/dataset1_guided_fixations.h5 models/dataset5_free_viewing.h5 ## gets all pretrained models from OSF

models/dataset1_guided_fixations.h5:
	mkdir -p models
	wget -q https://osf.io/download/cqf74/ -O models/dataset1_guided_fixations.h5

models/dataset5_free_viewing.h5:
	mkdir -p models
	wget -q https://osf.io/download/89nky/ -O models/dataset5_free_viewing.h5


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
	sphinx-apidoc -o docs/source bidsmreye
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .


## TESTS

test: models tests/data/moae_fmriprep ## run tests quickly with the default Python
	python -m pytest --cov bidsmreye

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

demo: clean-demo tests/data/moae_fmriprep models/dataset1_guided_fixations.h5 ## demo: runs all demo steps on MOAE dataset
	bidsmreye 	--action all \
				--verbosity INFO \
				--debug true \
				--reset_database true \
				$$PWD/tests/data/moae_fmriprep \
				$$PWD/outputs/moae_fmriprep/derivatives \
				participant

prepare: tests/data/moae_fmriprep models/dataset1_guided_fixations.h5 ## demo: prepares the data of MOAE dataset
	bidsmreye 	--action prepare \
				--verbosity INFO \
				--debug true \
				--reset_database true \
				$$PWD/tests/data/moae_fmriprep \
				$$PWD/outputs/moae_fmriprep/derivatives \
				participant

combine: ## demo: combines data and dummy labels of MOAE dataset
	bidsmreye 	--action combine \
				--verbosity INFO \
				--debug true \
				--reset_database true \
				$$PWD/tests/data/moae_fmriprep \
				$$PWD/outputs/moae_fmriprep/derivatives \
				participant

generalize: ## demo: predicts labels of MOAE dataset
	bidsmreye 	--model guided_fixations \
				--action generalize \
				--verbosity INFO \
				--debug true \
				--reset_database true \
				$$PWD/tests/data/moae_fmriprep \
				$$PWD/outputs/moae_fmriprep/derivatives \
				participant


## Openneuro data
.PHONY: get_ds002799_dat

clean-ds002799:
	rm -fr outputs/ds002799/derivatives

tests/data/data_ds002799:
	datalad install -s ///openneuro/ds002799 tests/data/ds002799

get_ds002799: tests/data/data_ds002799
	cd tests/data/ds002799/derivatives/fmriprep && \
	datalad get sub-30[27]/ses-*/func/*run-*preproc*bold*

ds002799_prepare: get_ds002799 models/dataset1_guided_fixations.h5
	bidsmreye 	--action prepare \
				--verbosity INFO \
				$$PWD/tests/data/ds002799/derivatives/fmriprep \
				$$PWD/outputs/ds002799/derivatives \
				participant \
				--participant_label 302 307 \
				--space MNI152NLin2009cAsym T1w \
				--run 1 2

ds002799_combine:
	bidsmreye 	--action combine \
				--verbosity INFO \
				$$PWD/tests/data/ds002799/derivatives/fmriprep \
				$$PWD/outputs/ds002799/derivatives \
				participant \
				--participant_label 302 307 \
				--space MNI152NLin2009cAsym T1w \
				--run 1 2

ds002799_generalize:
	bidsmreye 	--action generalize \
				--verbosity INFO \
				$$PWD/tests/data/ds002799/derivatives/fmriprep \
				$$PWD/outputs/ds002799/derivatives \
				participant \
				--participant_label 302 307 \
				--space MNI152NLin2009cAsym T1w \
				--run 1 2

ds002799: clean-ds002799
	bidsmreye 	--action all \
				--verbosity INFO \
				$$PWD/tests/data/ds002799/derivatives/fmriprep \
				$$PWD/outputs/ds002799/derivatives \
				participant \
				--participant_label 302 307 \
				--space MNI152NLin2009cAsym T1w \
				--run 1 2


## DOCKER
.PHONY: docker/Dockerfile docker/Dockerfile_dev

docker/Dockerfile: ## Dockerfile for the bidsmreye docker image
	docker run --rm repronim/neurodocker:0.7.0 generate docker \
	--base debian:stretch-slim \
	--pkg-manager apt \
	--install "git wget make" \
	--miniconda \
		create_env="bidsmreye" \
		conda_install="python=3.9 pip" \
		activate="true" \
		pip_install="git+https://github.com/cpp-lln-lab/bidsMReye.git" \
	--run "mkdir -p /home/neuro/bidsMReye" \
	--copy Makefile /home/neuro/bidsMReye \
	--workdir /home/neuro/bidsMReye \
 	--run "make models" \
	--copy ./docker/entrypoint.sh /neurodocker/startup.sh \
	--run "chmod +x /neurodocker/startup.sh" \
	--cmd bidsmreye \
	> docker/Dockerfile

docker_build: docker/Dockerfile
	docker build --tag cpplab/bidsmreye:latest --file docker/Dockerfile .

docker/Dockerfile_dev: ## Dockerfile for the bidsmreye docker image using local pacakge
	docker run --rm repronim/neurodocker:0.7.0 generate docker \
	--base debian:stretch-slim \
	--pkg-manager apt \
	--install "git wget make" \
	--miniconda \
		create_env="bidsmreye" \
		conda_install="python=3.9 pip" \
		activate="true" \
	--run "mkdir -p /home/neuro/bidsMReye" \
	--copy . /home/neuro/bidsMReye \
	--workdir /home/neuro/bidsMReye \
 	--run "make models" \
	--miniconda \
		use_env="bidsmreye" \
		pip_install="." \
	--copy ./docker/entrypoint.sh /neurodocker/startup.sh \
	--run "chmod +x /neurodocker/startup.sh" \
	--cmd bidsmreye \
	> docker/Dockerfile_dev

docker_dev_build: docker/Dockerfile_dev
	docker build --tag cpplab/bidsmreye:dev --file docker/Dockerfile_dev .

docker_dev_build_no_cache: docker/Dockerfile_dev
	docker build --tag bidsmreye:dev --no-cache --file docker/Dockerfile_dev .

docker_demo: Docker_build clean-demo
	make Docker_prepare_data
	make Docker_combine
	make Docker_generalize

docker_prepare_data:
	docker run --rm -it \
				--user "$(id -u):$(id -g)" \
				-v $$PWD/tests/data/moae_fmriprep:/home/neuro/data \
				-v $$PWD/outputs:/home/neuro/outputs \
				bidsmreye:latest \
				/home/neuro/data/ \
				/home/neuro/outputs/ \
				participant \
				--action prepare

docker_combine:
	docker run --rm -it \
				--user "$(id -u):$(id -g)" \
				-v $$PWD/tests/data/moae_fmriprep:/home/neuro/data \
				-v $$PWD/outputs:/home/neuro/outputs \
				bidsmreye:latest \
				/home/neuro/data/ \
				/home/neuro/outputs/ \
				participant \
				--action combine

docker_generalize:
	docker run --rm -it \
				--user "$(id -u):$(id -g)" \
				-v $$PWD/tests/data/moae_fmriprep:/home/neuro/data \
				-v $$PWD/outputs:/home/neuro/outputs \
				bidsmreye:latest \
				/home/neuro/data/ \
				/home/neuro/outputs/ \
				participant \
				--action generalize
