#!/usr/bin/python
# pylint: disable=W0142
"""
terracotta.* scripts item

This file is part of ZTC and distributed under GNU GPL v.3
Copyright (c) 2011 Vladimir Rusinov]
"""

from ztc.java.terracotta import JMXTerracotta

j = JMXTerracotta()
m = j.args[0]
j.get(m, *j.args[1:])
