#!/bin/python3

import argparse
import glob
import hashlib
import logging
import os
import sys
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(
    description="Check integrity of redump PlayStation bin/cue files.")
parser.add_argument("-d", "--datfile", type=str,
                    required=True, help="Path to the reference datfile.")
parser.add_argument("-c", "--check-dir", type=str,
                    required=True, help="Path to the directory to check.")
args = parser.parse_args()

logging.root.setLevel(logging.NOTSET)
logger = logging.getLogger(__name__)

h1 = logging.StreamHandler(sys.stderr)
h1.setLevel(logging.WARNING)
h1.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
h1.addFilter(lambda x: x.levelno == logging.WARNING)
h2 = logging.StreamHandler(sys.stdout)
h2.setLevel(logging.INFO)
h2.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
h2.addFilter(lambda x: x.levelno != logging.WARNING)

logger.addHandler(h1)
logger.addHandler(h2)


def load_and_parse_datfile(path):
    try:
        tree = ET.parse(path)
    except OSError as err:
        logger.error("Could not open datfile %s: %s.", path, err)
        return None
    except ET.ParseError as err:
        logger.error("Could not parse XML: %s", err)
        return None

    return tree.getroot()


def build_sha1_to_name_dict(parsed_datfile):
    roms = {}
    for game in parsed_datfile:
        for rom in [x for x in game if x.tag == 'rom']:
            roms[rom.attrib['sha1']] = rom.attrib['name']
    return roms


def bin_and_cue_files(search_dir):
    return filter(lambda x: os.path.splitext(x)[1] in ['.bin', '.cue'],
                  glob.iglob(os.path.join(search_dir, '**'), recursive=True))


def next_chunk(f, chunk_size=4096):
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        yield chunk


def main(_args):
    logger.info("Parsing datfile '%s' ...", _args.datfile)
    datfile = load_and_parse_datfile(_args.datfile)
    if not datfile:
        logger.critical("No datfile - aborting.")
        sys.exit(1)

    logger.info("Building sha1-to-name dict ...")
    roms = build_sha1_to_name_dict(datfile)
    if not roms:
        logger.critical("No reference data - aborting.")
        sys.exit(1)

    logger.info("Checking file integrity ...")
    checked_files_count = 0
    bad_files_count = 0
    skipped_files_count = 0
    for _file in bin_and_cue_files(_args.check_dir):
        file_hash = ''
        sha1 = hashlib.sha1()
        try:
            with open(_file, 'rb') as f:
                for chunk in next_chunk(f):
                    sha1.update(chunk)
            file_hash = sha1.hexdigest()
        except OSError as err:
            logger.error("Could not open file '%s', skipping: %s", _file, err)
            skipped_files_count += 1
        else:
            if file_hash not in roms:
                logger.warning("%s | %s | not found", _file, file_hash)
                bad_files_count += 1
            checked_files_count += 1

    logger.info("Done; integrity of %u files was checked, of which %u files did not match any redump hash. %u files were skipped.",
                checked_files_count, bad_files_count, skipped_files_count)


if __name__ == "__main__":
    main(args)
