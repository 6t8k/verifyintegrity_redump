#!/bin/python3

import argparse
import collections
import glob
import hashlib
import json
import logging
import os
import sys
import xml.etree.ElementTree as ET

DEF_CHECK_FNAME_EXTS = "bin,cue"
DEF_CHUNKSIZE = 4096

parser = argparse.ArgumentParser(
    description="Verify integrity of disc images against a Redump datfile.")
parser.add_argument("-d", "--datfile", type=str,
                    required=True, help="Path to the reference datfile.")
parser.add_argument("-c", "--check-dir", type=str,
                    required=True, help="Path to the directory to check.")
parser.add_argument("-f", "--filename-extensions", type=str,
                    default=DEF_CHECK_FNAME_EXTS, help="Comma-separated list"
                    " of filename extensions (without leading '.'). This"
                    " script will only examine files the names of which have"
                    " these extensions. Default value: '{}'".format(DEF_CHECK_FNAME_EXTS))
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


def files_to_verify(search_dir, check_fname_exts):
    return filter(lambda x: x[1] in check_fname_exts,
                  ((y, os.path.splitext(y)[1]) for y in glob.iglob(os.path.join(search_dir, '**'), recursive=True)))


def next_chunk(f, chunk_size=DEF_CHUNKSIZE):
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        yield chunk


def main(_args):
    logger.info("Starting with arguments: %s", vars(_args))

    checked_files_count = collections.defaultdict(int)
    bad_files_count = collections.defaultdict(int)
    skipped_files_count = collections.defaultdict(int)
    check_fname_exts = ['.{}'.format(x)
                        for x in _args.filename_extensions.split(',')]

    logger.info("Parsing datfile ...")
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
    for _file, ext in files_to_verify(_args.check_dir, check_fname_exts):
        file_hash = ''
        sha1 = hashlib.sha1()
        try:
            with open(_file, 'rb') as f:
                for chunk in next_chunk(f):
                    sha1.update(chunk)
            file_hash = sha1.hexdigest()
        except OSError as err:
            logger.error("Could not open file '%s', skipping: %s", _file, err)
            skipped_files_count[ext] += 1
        else:
            if file_hash not in roms:
                logger.warning("%s | %s | not found",
                               json.dumps(_file), file_hash)
                bad_files_count[ext] += 1
            checked_files_count[ext] += 1

    logger.info("Done; checked files: %s, bad files: %s, skipped files: %s.",
                dict(checked_files_count), dict(bad_files_count), dict(skipped_files_count))


if __name__ == "__main__":
    main(args)
