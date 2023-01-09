#!/usr/bin/env bash

# Replaces the default entrypoint.sh created by neurodocker with a custom one
# that runs bidsmreye on startup.

set -e
export USER="${USER:=$(whoami)}"
if [ -n "$1" ]; then bidsmreye "$@"; else bidsmreye --help; fi
