#!/usr/bin/env python
""" ztc.sytstem.vfs test"""

import unittest

from ztc.system.vfs import DiskStats, DiskStatsParser


class DiskStatsParserTest(unittest.TestCase):

    def setUp(self):
        import logging
        self.logger = logging.getLogger('test')

    def test_diskstats_line_parser(self):
        """ Test parsing of /proc/diskstats file """
        dsp = DiskStatsParser('sda', self.logger)
        ds = DiskStats()

        # 1: simple sda line from 3.1.x kernel
        ds.major = 8
        ds.minor = 0
        ds.devname = 'sda'
        ds.reads = 148516
        ds.reads_merged = 118319
        ds.sectors_read = 7024128
        ds.time_read = 1863284
        ds.writes = 116304
        ds.writes_merged = 375629
        ds.sectors_written = 11643968
        ds.time_write = 17513572
        ds.cur_ios = 0
        ds.time_io = 1429389
        ds.time_io_weidged = 19461480
        assert str(dsp._parse_diskstats_line('   8       0 sda 148516 118319 '
                                             '7024128 1863284 116304 375629 '
                                             '11643968 17513572 0 1429389 '
                                             '19461480')) == str(ds)

        # 2: test for device with '/' in name
        # 104 0 cciss/c0d0 12746 1947 208311 37832 2424476 2120977 36390792 \
        #     58162004 0 24766012 58198856
        ds.major = 104
        ds.minor = 0
        ds.devname = 'cciss/c0d0'
        ds.reads = 12746
        ds.reads_merged = 1947
        ds.sectors_read = 208311
        ds.time_read = 37832
        ds.writes = 2424476
        ds.writes_merged = 2120977
        ds.sectors_written = 36390792
        ds.time_write = 58162004
        ds.cur_ios = 0
        ds.time_io = 24766012
        ds.time_io_weidged = 58198856
        assert str(dsp._parse_diskstats_line('104 0 cciss/c0d0 12746 1947 '
                                             ' 208311 37832 2424476 2120977 '
                                             '36390792 58162004 0 24766012 '
                                             '58198856')) == str(ds)
