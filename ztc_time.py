#!/usr/bin/python
"""
ZTC ntp jitter item script

Copyright (c) 2010-2012 Vladimir Rusinov <vladimir@greenmice.info>
Copyright (c) 2010 Murano Software [http://muranosoft.com]
Copyright (c) 2010 Docufide, Inc. [http://docufide.com]
Copyright (c) 2011 Wrike, Inc [http://www.wrike.com]
License: GNU GPL v3
"""

from ztc.system.ntp_time import TimeCheck

t = TimeCheck()
m = t.args[0]
t.get(m)
