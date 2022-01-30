- [CONTRIBUTING](#contributing)
    - [Types of Contributions](#types-of-contributions)
        - [Report Bugs](#report-bugs)
        - [Fix Bugs](#fix-bugs)
        - [Implement Features](#implement-features)
        - [Write Documentation](#write-documentation)
        - [Submit Feedback](#submit-feedback)
    - [Get Started!](#get-started)
    - [Pull Request Guidelines](#pull-request-guidelines)
    - [Tips](#tips)
    - [Deploying](#deploying)
    - [Docker recipe](#docker-recipe)

# CONTRIBUTING

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at https://github.com/Remi-Gau/bidsmreye/issues.

If you are reporting a bug, please include:

-   Your operating system name and version.
-   Any details about your local setup that might be helpful in troubleshooting.
-   Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

### Write Documentation

bidsMReye could always use more documentation, whether as part of the
official bidsMReye docs, in docstrings, or even on the web in blog posts,
articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/Remi-Gau/bidsmreye/issues.

If you are proposing a feature:

-   Explain in detail how it would work.
-   Keep the scope as narrow as possible, to make it easier to implement.
-   Remember that this is a volunteer-driven project, and that contributions
    are welcome :)

## Get Started!

Ready to contribute? Here's how to set up `bidsmreye` for local development.

1. Fork the `bidsmreye` repo on GitHub.
2. Clone your fork locally:

```bash
git clone git@github.com:your_name_here/bidsmreye.git
```

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development:

```bash
mkvirtualenv bidsmreye
cd bidsmreye/
python setup.py develop
```

1. Create a branch for local development:

```bash
git checkout -b name-of-your-bugfix-or-feature
```

Now you can make your changes locally.

2. When you're done making changes, check that your changes pass flake8 and the
   tests, including testing other Python versions with tox:

```bash
flake8 bidsmreye tests
python setup.py test or pytest
tox
```

To get flake8 and tox, just pip install them into your virtualenv.

3. Commit your changes and push your branch to GitHub:

```bash
git add .
git commit -m "Your detailed description of your changes."
git push origin name-of-your-bugfix-or-feature
```

4. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.8, and for PyPy. Check
   https://travis-ci.com/Remi-Gau/bidsmreye/pull_requests
   and make sure that the tests pass for all supported Python versions.

## Tips

To run a subset of tests:

```bash
pytest tests.test_bidsmreye
```

## Deploying

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.rst).

Then run

```bash
bump2version patch # possible: major / minor / patch
git push
git push --tags
```

Travis will then deploy to PyPI if tests pass.

## Docker recipe

Made using neurodocker

```bash
docker run --rm repronim/neurodocker:0.7.0 generate docker \
    --base debian:bullseye-slim \
    --pkg-manager apt \
    --install "git wget" \
    --miniconda \
        version="latest" \
        create_env="deepmreye" \
        conda_install="python=3.7 pip" \
        pip_install="git+https://github.com/DeepMReye/DeepMReye.git" \
        activate="true" \
    --run "mkdir -p /inputs/models" \
    --run "wget https://osf.io/cqf74/download -O /inputs/models/dataset1_guided_fixations.h5" \
    --output Dockerfile
```

Build image

```bash
docker build --tag deepmreye:0.1.0 --file Dockerfile .
```

Run it

```bash
docker run -it --rm \
    deepmreye:0.1.0
```
