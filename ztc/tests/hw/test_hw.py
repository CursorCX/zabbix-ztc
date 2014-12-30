#!/usr/bin/env python
#pylint: disable=W0212
"""
test for ztc.hw.RAID_3Ware

This file is part of ZTC

Copyright (c) 2012 Wrike, Inc. [http://www.wrike.com/]
"""

import unittest
from ztc.hw import RAID_3Ware


class TestRAID_3Ware(unittest.TestCase):
    """ Tests for RAID_3Ware class """

    def test_get_status(self):
        """ test parsing of status output """
        key = (0, 0, 'status')
        r = RAID_3Ware(test=True)

        # 1: Ok message
        r._tw_out[key] = "/c0/u0 status = OK\n\n"
        self.assertEquals(r.get_status(), 'OK')

        # 2: fail message
        r._tw_out[key] = "/c0/u0 status = FAIL"
        self.assertEquals(r.get_status(), 'FAIL')

        # 3: no message
        r._tw_out[key] = ""
        self.assertEquals(r.get_status(), 'ZTC_FAIL: TW_CLI')

        # 4: wrong type
        r._tw_out[key] = ()
        self.assertEquals(r.get_status(), 'ZTC_FAIL: popen')
        r._tw_out[key] = None
        self.assertEquals(r.get_status(), 'ZTC_FAIL: popen')
        r._tw_out[key] = 123
        self.assertEquals(r.get_status(), 'ZTC_FAIL: popen')

if __name__ == '__main__':
    unittest.main()
