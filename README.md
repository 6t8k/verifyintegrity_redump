verifyintegrity\_redump
=====================

This is a Python script that automates verification of disk image integrity against hashes provided by the redump project.

You need Python 3, there are no other software dependencies.

Basic usage
----------

1. Download the datfile appropriate for the console you'd like to verify disk images for. These are available here: [http://redump.org/downloads/](http://redump.org/downloads/). Please note that redump.org does not provide any disk images.

2. Invoke verifyintegrity\_redump:

```verifyintegrity_redump.py -d path/to/your/datfile.dat -c path/to/your/disc/image/directory/```

The directory given by means of the `-c` argument is descended recursively and for all files found the names of which end in `.bin` or `.cue`, verification against the datfile given by means of the `-d` argument is attempted.

General status messages are output to `stdout`, file paths for which verification yields a negative result are output to `stderr`.

Limitations
-----------

- Currently, only .bin/.cue images are supported.

Other remarks
-------------

Because cuesheets contain the name(s) of the corresponding `.bin` file(s), it's possible that verification yields a negative result for some cuesheets belonging to disk images that were renamed by the redump project at a later point in time. This is usually not a problem - if in doubt you can compare manually against the cuesheets provided by the redump project.

