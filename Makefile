.PHONY: clean clean-build clean-pyc clean-test coverage dist docs help install lint lint/flake8 lint/black Dockerfile_dev
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

clean-models:
	rm -fr models/

lint/flake8: ## check style with flake8
	flake8 bidsmreye tests
lint/black: ## check style with black
	black bidsmreye tests
lint/mypy: ## check style with mypy
	mypy bidsmreye

lint: lint/black lint/mypy lint/flake8  ## check style

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/source/bidsmreye.rst
	rm -f docs/source/modules.rst
	sphinx-apidoc -o docs/source bidsmreye
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

## TESTS

test: models tests/data/moae_fmriprep ## run tests quickly with the default Python
	python -m pytest --cov bidsmreye

# python -m pytest --cov bidsmreye # --cov-report html:htmlcov
# $(BROWSER) htmlcov/index.html

tests/data/moae_fmriprep:
	mkdir -p tests/data
	wget -q https://osf.io/vufjs/download
	unzip download
	rm download
	mv moae_fmriprep tests/data/moae_fmriprep

## PRE-TRAINED MODELS
models: models/dataset1_guided_fixations.h5 models/dataset5_free_viewing.h5

models/dataset1_guided_fixations.h5:
	mkdir -p models
	wget https://osf.io/download/cqf74/ -O models/dataset1_guided_fixations.h5

models/dataset5_free_viewing.h5:
	mkdir -p models
	wget https://osf.io/download/89nky/ -O models/dataset5_free_viewing.h5


## DEMO

demo: clean-demo
	make prepare_data
	make combine
	make generalize

prepare_data: tests/data/moae_fmriprep models/dataset1_guided_fixations.h5
	bidsmreye 	--space MNI152NLin6Asym \
				--task auditory \
				--action prepare \
				--verbosity WARNING \
				--debug True \
				$$PWD/tests/data/moae_fmriprep \
				$$PWD/outputs participant\


combine:
	bidsmreye 	--space MNI152NLin6Asym \
				--task auditory \
				--action combine \
				--verbosity INFO \
				--debug False \
				$$PWD/tests/data/moae_fmriprep \
				$$PWD/outputs participant

generalize:
	bidsmreye 	--space MNI152NLin6Asym \
				--task auditory \
				--model guided_fixations \
				--action generalize \
				--verbosity INFO \
				--debug False \
				$$PWD/tests/data/moae_fmriprep \
				$$PWD/outputs participant

clean-demo:
	rm -fr outputs

## DOCKER

Dockerfile_dev:
	docker run --rm repronim/neurodocker:0.7.0 generate docker \
	--base debian:stretch-slim \
	--pkg-manager apt \
	--install "git wget make" \
	--user neuro \
	--miniconda \
		create_env="bidsmreye" \
		conda_install="python=3.9 pip" \
		activate="true" \
	--run "mkdir -p /home/neuro/bidsMReye" \
	--copy . /home/neuro/bidsMReye \
	--workdir /home/neuro/bidsMReye \
	--miniconda \
		use_env="bidsmreye" \
		pip_install="." \
	--run "chmod "+x" /home/neuro/bidsMReye/docker_entrypoint.sh" \
	--entrypoint /home/neuro/bidsMReye/docker_entrypoint.sh \
	> Dockerfile_dev

# --run "make models"
Docker_dev_build: Dockerfile_dev
	docker build --tag bidsmreye:dev --file Dockerfile_dev .

Docker_dev_build_no_cache: Dockerfile_dev
	docker build --tag bidsmreye:dev --no-cache --file Dockerfile_dev .

Docker_demo_prepare_data:
	docker run --rm -it \
				-v $$PWD/tests/data/moae_fmriprep:/home/neuro/data \
				-v $$PWD/outputs:/home/neuro/outputs \
				bidsmreye:dev \
				/home/neuro/data/ \
				/home/neuro/outputs/ \
				participant \
				--action prepare
