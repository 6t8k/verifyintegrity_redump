# verifyintegrity\_redump

This is a Python script that automates verification of disc image integrity against hashes provided by the Redump disc preservation project.

You need Python 3, there are no other software dependencies.

## Basic usage

1. Download the datfile appropriate for the console you'd like to verify disc images for. These are available here: [http://redump.org/downloads/](http://redump.org/downloads/). Please note that redump.org does not provide any disc images.

2. Invoke verifyintegrity\_redump:

```verifyintegrity_redump.py -d path/to/your/datfile.dat -c path/to/your/disc/image/directory/ -f bin,cue```

The directory given by means of the `-c` argument is descended recursively and for all files found the names of which end in `.bin` or `.cue`, verification against the datfile given by means of the `-d` argument is attempted. Only files the filename extensions of which are contained in the comma-separated list given by means of the `-f` option are considered. For example, if `-f iso` is used, verification is attempted only for files the names of which end in `.iso`. If the `-f` option is omitted, `-f bin,cue` is assumed by default.

General status messages are output to `stdout`, file paths for which verification yields a negative result are output to `stderr`.

## Limitations

- Currently, files that don't have a filename extension, i.e. e.g. `a-directory/a-filename`, or verifying all files in one directory regardless of their names in one go, is not supported.

## Other remarks

Because cuesheets contain the name(s) of the corresponding `.bin` file(s), it's possible that verification yields a negative result for some cuesheets belonging to disc images that were renamed by the Redump project at a later point in time. This is usually not a problem - if in doubt you can compare manually against the cuesheets provided by the Redump project.

