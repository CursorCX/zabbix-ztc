#!/usr/bin/env python
#pylint: disable=R0904
""" Test for ZTCCheck class """

import unittest

from ztc.check import ZTCCheck
from ztc.tests import setup_no_logging

ZTCCheck._setup_logging = setup_no_logging


class ZTCCheckTest(unittest.TestCase):
    """ Test for ZTCCheck class """

    class ZTCTestCheck(ZTCCheck):
        name = 'test'

        def _get(self, *args, **kwargs):
            if len(args) == 1:
                return args[0]

    def test_floatformat(self):
        """ Zabbix only accepts floating-point numbers in xx.xx format.
        Test that we are returning correct string for every float """

        ch = self.ZTCTestCheck()
        self.assertEqual(ch.get_val(8.1e-05), '0.000081')
        self.assertEqual(ch.get_val(100000.0), '100000')
        self.assertEqual(ch.get_val(0.0), '0')
        self.assertEqual(ch.get_val(0.33333333333333333333333), '0.333333')
