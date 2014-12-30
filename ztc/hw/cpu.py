#!/usr/bin/env python
"""
ZTC Cpu hardware checks

This file is part of ZTC and distributed under the same license.

Copyright (c) 2011 Wrike, Inc. [http://www.wrike.com/]
Copyright (c) 2010 Vladimir Rusinov <vladimir@greenmice.info>
"""

import re

from ztc.check import ZTCCheck
from ztc.myos import popen


class CPUTemperature(ZTCCheck):
    name = "cputemp"

    # pylint: disable=W0613
    def _get(self, metric, *arg, **kwarg):
        # metric could be ommited
        t = self.get_temp_acpi()
        if t:
            return t
        t = self.get_temp_lm_sensors()
        if t:
            return t
        return -1

    def get_temp_acpi(self):
        """ get cpu temperature from ACPI thermal zone """
        self.logger.debug("getting cpu temp from acpi")
        try:
            f = open('/proc/acpi/thermal_zone/THRM/temperature', 'r')
            lines = f.readlines()
            ret = int(lines[-1].split()[-2])
            f.close()
            return ret
        # pylint: disable=W0702
        except:
            self.logger.exception("get_temp_acpi failed")
            return None

    def get_temp_lm_sensors(self):
        """ try to get temperature from lm_sensors file
        example outputs:
coretemp-isa-0000
Core 0:      +81.0 C  (high = +100.0 C, crit = +100.0 C)

coretemp-isa-0001
Core 1:      +82.0 C  (high = +100.0 C, crit = +100.0 C)
        """
        self.logger.debug("getting cpu temp from lm_sensors")
        try:
            n = 0
            tot_temp = 0.0
            #temp_re = re.compile('(\d+.\d+) C')
            temp_re = re.compile('^Core [0-9]+: +\+([0-9]+(\.[0-9]+)?)')
            cmd = 'sensors -A'
            for l in popen(cmd, self.logger)[1].split("\n"):
                self.logger.debug("lm_sensors line: %s" % (l,))
                temps = temp_re.findall(l)
                self.logger.debug("temps = %s" % (temps,))
                if temps:
                    temp = float(temps[0][0])
                    tot_temp += temp
                    n += 1
            if n == 0:
                return None
            return tot_temp / n
        # pylint: disable=W0703
        except Exception, e:
            self.logger.debug("failed: %s" % (str(e),))
            return None
