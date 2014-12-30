#!/usr/bin/env python
"""ztc.vm.memory tests"""

import unittest

from ztc.vm.memory import Memory


class Test(unittest.TestCase):

    def test_get_active(self):
        m = Memory()
        assert isinstance(m.active, long)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
