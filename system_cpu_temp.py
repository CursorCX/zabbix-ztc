#!/usr/bin/python
"""
system_cpu_temp - get cpu temperature

This file is part of ztc, http://bitbucket.org/rvs/ztc/
Licensed under GPL v.3
Copyright (c) 2010 Vladimir Rusinov <vladimir@greenmice.info>
Copyright (c) 2011 Wrike, Inc. [http://www.wrike.com]
"""

from ztc.hw.cpu import CPUTemperature

c = CPUTemperature()
c.get('temperature')
