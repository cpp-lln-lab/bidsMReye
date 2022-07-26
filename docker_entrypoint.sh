#!/usr/bin/env bash
set -e
export USER="${USER:=$(whoami)}"
source activate bidsmreye
if [ -n "$1" ]; then bidsmreye "$@"; else bidsmreye --help; fi
