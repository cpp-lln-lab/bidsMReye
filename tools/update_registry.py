from __future__ import annotations

import os

import pooch

# from https://www.fatiando.org/pooch/latest/registry-files.html

# Names and urls of the data files. The file names are used for naming the
# downloaded files. These are the names that will be included in the registry.
fnames_and_urls = {
    "datasets_1to5.h5": "https://osf.io/download/23t5v/",
    "datasets_1to6.h5": "https://osf.io/download/mr87v/",
}

# Create a new directory where all files will be downloaded
directory = "data_files"
os.makedirs(directory)

# Create a new registry file
with open("registry.txt", "w") as registry:
    for fname, url in fnames_and_urls.items():
        # Download each data file to the specified directory
        path = pooch.retrieve(
            url=url, known_hash=None, fname=fname, path=directory, progressbar=True
        )
        # Add the name, hash, and url of the file to the new registry file
        registry.write(f"{fname} {pooch.file_hash(path)} {url}\n")
