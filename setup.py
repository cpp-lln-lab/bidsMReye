#!/usr/bin/env python
import sys

from setuptools import find_packages
from setuptools import setup

# Give setuptools a hint to complain if it's too old a version
# 30.3.0 allows us to put most metadata in setup.cfg
# Should match pyproject.toml
SETUP_REQUIRES = ["setuptools >= 30.3.0"]
# This enables setuptools to install wheel on-the-fly
SETUP_REQUIRES += ["wheel"] if "bdist_wheel" in sys.argv else []

long_description = open("README.md").read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()


if __name__ == "__main__":

    setup(
        name="bidsmreye",
        version="0.1.0",
        install_requires=requirements,
        setup_requires=SETUP_REQUIRES,
        author="Remi Gau",
        author_email="remi.gay@gmail.com",
        description="bids app using deepMReye to decode eye motion for fMRI time series data",
        long_description=long_description,
        url="https://github.com/cpp-lln-lab/bidsMReye",
        license="LGPL-3.0",
        classifiers=[
            "Development Status :: 3 - Alpha",
            "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
            "Natural Language :: English",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
        ],
        packages=find_packages(),
    )
