#!/usr/bin/python
"""
jmx.* scripts item

Copyright (c) 2011 Vladimir Rusinov <vladimir@greenmice.info>
License: GNU GPL3
This file is part of ZTC
"""

from ztc.java.jmx import JMXCheck

j = JMXCheck()
m = j.args[0]
j.get(m, *j.args[1:])
