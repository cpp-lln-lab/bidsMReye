#!/usr/bin/env python
import sys

from setuptools import setup


SETUP_REQUIRES = ["setuptools >= 30.3.0"]
SETUP_REQUIRES += ["wheel"] if "bdist_wheel" in sys.argv else []

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

if __name__ == "__main__":

    setup(
        install_requires=requirements,
        setup_requires=SETUP_REQUIRES,
    )
