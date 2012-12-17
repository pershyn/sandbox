#!/usr/bin/env python3

"""
This module contains implementations for
basic cable optimizer unit test
"""

import unittest

# add current folder to system path
import os
import sys
import inspect

cmd_folder = os.path.realpath(os.path.abspath(os.path.split(
    inspect.getfile(inspect.currentframe()))[0]))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

import cable_optimizer


class CableOptimizerTest(unittest.TestCase):
    """ unit test for module """

    def setUp(self):
        self.e1 = [["a", "e", 2],
                   ["e", "b", 2],
                   ["a", "c", 0],
                   ["c", "d", 8],
                   ["c", "d", 8],
                   ["d", "b", 0]]

        self.e1sorted = [["a", "e", 2],
                         ["b", "e", 2],
                         ["a", "c", 0],
                         ["c", "d", 8],
                         ["c", "d", 8],
                         ["b", "d", 0]]

        self.e2 = [["a", "k", 1],
                   ["k", "c", 2],
                   ["k", "d", 2],
                   ["c", "e", 3],
                   ["c", "d", 4],
                   ["d", "f", 6],
                   ["a", "g", 7],
                   ["f", "g", 8],
                   ["g", "h", 9],
                   ["h", "b", 10],
                   ["b", "e", 11],
                   ["f", "b", 12],
                   ["d", "e", 13]]

    def test_redirect_edge(self):
        res = ['b', 'a', 4]
        exp = ['a', 'b', 4]
        cable_optimizer.redirect_edge_alpabetically(res)
        self.assertEqual(exp, res)

        res = ['e', 'z', 4]
        exp = ['e', 'z', 4]
        cable_optimizer.redirect_edge_alpabetically(res)
        self.assertEqual(exp, res)

    def test_eliminate_zero_edges(self):
        cable_optimizer.eliminate_zero_edges(self.e1sorted, 'a', 'b')
        expected = [['a', 'e', 2], ['b', 'e', 2], ['a', 'b', 8], ['a', 'b', 8]]
        self.assertEqual(self.e1sorted, expected)

    def test_get_transition_vertices(self):
        dd = {'a': [2, 0, 2], 'c': [3, 2, 3, 4], 'b': [2, 1, 5],
              'e': [2, 0, 1], 'd': [3, 3, 4, 5]}
        expected = {'e': [0, 1]}
        real = cable_optimizer.get_transition_vertexes(dd, 'a', 'b')
        self.assertEqual(real, expected)

    def test_optimize(self):
        res = self.e1  # optimize will modify e1
        exp = [['a', 'b', 2]]
        cable_optimizer.optimize(res, 'a', 'b')
        self.assertEqual(exp, res)


if __name__ == "__main__":
    unittest.main()
