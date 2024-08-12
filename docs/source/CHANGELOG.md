# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security
-->

## [Unreleased]

### Added

* [ENH] Extra metadata have been added to the output of the `generalize` step to better align with BIDS BEP20 @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/232

### Changed

* [ENH] Output filenames of the prepare step has been changed to use the `timeseries` suffix and the output of the `generalize` step now include the name of the Deepmreye model used to compute them @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/232

### Deprecated

### Removed

### Fixed

* [FIX] do not apply run found for one task to all tasks by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/228

### Security


## [0.4.0] - 20234-08-05

* [FIX] update file naming when run indices are padded by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/146
* [MAINT] move most of the config to pyproject.toml by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/147
* [MAINT] update packaging by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/165
* [MAINT] pin pooch dependency by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/166
* [STY] use isort by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/191
* [FIX] pin keras and fix make file by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/197
* [FIX] fix deploy to github on Circle CI by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/210
* [ENH] improve error messages for invalid input data by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/150
* [ENH] turn `--action` into subcommands by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/215
* [ENH] Skip prepare and QC if output already exists by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/216
* [FIX] handle exceptions for QC at group level when participants are missing QC data by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/217
* [FIX]  Use repetition time from BIDS metadata instead of nifti header by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/218
* [FIX] save models in output dir by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/219
* [FIX] improve help for missing subject / task by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/220

**Full Changelog**: https://github.com/cpp-lln-lab/bidsMReye/compare/0.3.1...0.4.0

## [0.3.1] - 2023-01-23

* [ENH] update config by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/126
* [MNT] update docker and doc by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/118
* [FMT] format yml by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/120
* [INFRA] improve docker by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/122
* [DOC] update FAQ by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/121
* [DOC] add CLI info for group level by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/128

**Full Changelog**: https://github.com/cpp-lln-lab/bidsMReye/compare/0.3.0...0.4.0

## [0.3.0] - 2022-12-29

* [ENH] run QC on input data by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/113
* [ENH] add group level QA plot and table by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/115

**Full Changelog**: https://github.com/cpp-lln-lab/bidsMReye/compare/0.2.0...0.3.0

## [0.2.0] - 2022-12-19

* [DOC] add logo by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/89
* [MISC] by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/92
* [MNT] add workflow to run on openneuro data by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/90
* [ENH] improve log and change verbosity parameter by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/96
* [ENH] improve model download by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/97
* [ENH] improve methods by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/98
* [ENH] add CCO license by default by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/99
* [ENH] add possibility to used ANTs non linear registration by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/100
* [ENH] add basic QC by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/102

**Full Changelog**: https://github.com/cpp-lln-lab/bidsMReye/compare/0.1.2...0.2.0

## [0.1.0] - 2022-12-08

* [MNT] coverage, doc, config by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/20
* [ENH] save one output per subject by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/26
* [ENH] add CLI by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/28
* [REF] use Path instead of os.path by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/31
* [MNT] set up dev docker by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/32
* [ENH] use logging by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/34
* [ENH] Dockerfile make by @WeeXee in https://github.com/cpp-lln-lab/bidsMReye/pull/40
* [ENH] method section and vscode extensions by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/45
* [ENH] set up config class (Sourcery refactored) by @sourcery-ai in https://github.com/cpp-lln-lab/bidsMReye/pull/50
* [ENH] set up config class by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/48
* [ENH] run on several files by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/52
* [MISC] openneuro demo, add run argument, use pybids database... by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/58
* [ENH] downloads all models by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/60
* [FIX] do not specify nb args in argparse of CLI as leads to failure of constructing the config by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/63
* [MNT] prepare for pypi release by @Remi-Gau in https://github.com/cpp-lln-lab/bidsMReye/pull/85

### New Contributors

* @pre-commit-ci made their first contribution in https://github.com/cpp-lln-lab/bidsMReye/pull/1
* @Remi-Gau made their first contribution in https://github.com/cpp-lln-lab/bidsMReye/pull/20
* @sourcery-ai made their first contribution in https://github.com/cpp-lln-lab/bidsMReye/pull/27
* @WeeXee made their first contribution in https://github.com/cpp-lln-lab/bidsMReye/pull/40
* @allcontributors made their first contribution in https://github.com/cpp-lln-lab/bidsMReye/pull/46
* @Naubody made their first contribution in https://github.com/cpp-lln-lab/bidsMReye/pull/66
* @dependabot made their first contribution in https://github.com/cpp-lln-lab/bidsMReye/pull/70

**Full Changelog**: https://github.com/cpp-lln-lab/bidsMReye/commits/0.1.0
