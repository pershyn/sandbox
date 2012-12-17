'''
Utility script to clean old files in directory.

Scans the directory, finds files that are older than specified number of days
(by default, 30) and removes them. Adds record about that to log.

Intended to be used with python 3

Created on Mar 29, 2012
Edited on 2012-04-03

@version 0.0.4
@author: Mykhailo Pershyn
'''

import os
import time
from datetime import timedelta
import shutil
import argparse
import logging


def calculate_days_ago_in_sec(base_time_sec, days=30):
    month_in_sec = timedelta(days=days).total_seconds()
    month_ago_in_sec = base_time_sec - month_in_sec
    return month_ago_in_sec


def scantree_remove_empty_folders(path):
    """ Scan file tree and remove empty folders """
    for dirpath, dirnames, filenames in os.walk(path):
        if len(filenames) == 0 and len(dirnames) == 0:
            logger.info("Empty Folder found and removed: %s", dirpath)
            shutil.rmtree(dirpath)

        # pass folders to be scanned by same function (recursive)
        for dirname in dirnames:
            scantree_remove_empty_folders(os.path.join(dirpath, dirname))


def scantree_gen_files_to_removal(path, rm_time):
    """ Scan file tree and return files older than rm_time """
    for dirpath, dirnames, filenames in os.walk(path):

        # check the file dates in root folder
        for filename in filenames:
            fullPathToFile = os.path.join(dirpath, filename)
            filestat = os.stat(os.path.join(dirpath, filename))
            recent_access_time = filestat.st_atime
            if recent_access_time < rm_time:
                yield fullPathToFile

        # pass referenced folders to be scanned by same function (recursive)
        for dirname in dirnames:
            scantree_gen_files_to_removal(os.path.join(dirpath, dirname),
                                          rm_time)


def run_cleaner(path, rm_time):
    """ Run cleaner """
    logging.info("Searching files to removal in %s", path)
    for file in scantree_gen_files_to_removal(path, rm_time):
        logger.info("File to removal found: %s", file)
        try:
            os.remove(file)
        except:
            logger.info("Failed to remove file: %s, file skipped.", file)

    logger.info("Removing empty folders in %s", path)
    scantree_remove_empty_folders(path)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Clean specified folder from empty folders'
                    ' and files older than one month')
    parser.add_argument('path',
                        metavar='path',
                        type=str,
                        help='path to be cleaned recursively down the tree.'
                             'E.g. "C:\\testfolder"')
    return parser.parse_args()


def init_logger(path):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    logfile_name = os.path.join(path, "dircleaner.log")
    fileHandler = logging.FileHandler(filename=logfile_name)
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(
        logging.Formatter(fmt="%(asctime)s [%(levelname)s] - %(message)s",
                          datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(fileHandler)

    return logger


if __name__ == '__main__':

    args = parse_arguments()
    path = args.path
    rm_time = calculate_days_ago_in_sec(time.time())

    logger = init_logger(path)
    run_cleaner(path, rm_time)
