#!/usr/bin/env python
"""The setup script."""
from setuptools import find_packages
from setuptools import setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "Click>=7.0",
]

test_requirements = [
    "pytest>=3",
]

setup(
    author="Remi Gau",
    author_email="remi.gau@gmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="bids app using deepMReye to decode eye motion for fMRI time series data",
    entry_points={
        "console_scripts": [
            "bidsmreye=bidsmreye.cli:main",
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="bidsmreye",
    name="bidsmreye",
    packages=find_packages(include=["bidsmreye", "bidsmreye.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/Remi-Gau/bidsmreye",
    version="0.1.0",
    zip_safe=False,
)
