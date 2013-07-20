'''
Created on Apr 2, 2012

@author: Mykhailo.Pershyn
'''
import unittest
import os
from datetime import timedelta
import time
import dircleaner
import shutil


def create_tree(path, depth, amount):
    """ creates test tree of defined depth - empty folders """
    # depth 1 means this folder
    if depth < 1:
        return
    for i in range(amount):
        newpath = os.path.join(path, "test" + str(i))
        print("Creating folder: %s", newpath)
        os.mkdir(newpath)
        create_tree(newpath, depth - 1, amount)
    return


class TestDirCleaner(unittest.TestCase):


    path = "C:/dircleaner-testfolder/"


    def setUp(self):
        """ Create folder with bunch of files to test on """
        os.mkdir(self.path)
        create_tree(self.path, depth=2, amount=10)
        pass


    def tearDown(self):
        """ Clean the folder back """
        print("Removing test folder: %s", self.path)
        shutil.rmtree(self.path)
        pass


    def test_calculate_days_ago_in_sec(self):
        base = time.time()
        days = 10
        days_in_sec_expected = timedelta(days=days).total_seconds()
        days_ago_in_sec_expected = base - days_in_sec_expected
        days_real = dircleaner.calculate_days_ago_in_sec(base, days)
        self.assertEqual(days_ago_in_sec_expected, days_real,
                         "Days ago calculation is wrong")


    def test_scantree_remove_empty_folders(self):
        pass


    def test_scantree_gen_files_to_removal(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()