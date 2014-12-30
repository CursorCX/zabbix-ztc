#!/usr/bin/env python
"""Memory check class for ztc.

This file is part of ZTC and distributed under the same license

Copyright (c) 2011 Vladimir Rusinov <vladimir@greenmice.info>
"""

from ztc.check import ZTCCheck


class Memory(ZTCCheck):
    name = 'memory'

    def _get_amount(self, name):
        """ Get amount of %name% memory from /proc/meminfo
            @param name: memory metric name (string)
            @return: amount of requested memory metric, in bytes
        """
        f = open('/proc/meminfo', 'r')
        for l in f.readlines():
            if l.startswith('%s: ' % name):
                r = l.split()[-2]
        return long(r) * 1024

    @property
    def active(self):
        return self._get_amount('Active')

    @property
    def inactive(self):
        """ Get amount of inactive memory """
        return self._get_amount('Inactive')

    def get_used(self):
        """ Get amount of used (by apps) memory """
        return self._get_amount('MemTotal') - self._get_amount('MemFree') - \
            self._get_amount('Buffers') - self._get_amount('Cached')
    used = property(get_used)

if __name__ == '__main__':
    m = Memory()
    print "Used: ", m.used
    print "Active: ", m.active
    print "Inactive: ", m.inactive
