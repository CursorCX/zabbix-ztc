#!/usr/bin/python
# pylint: disable=W0142
"""
tomcat jmx proxy script

Copyright (c) 2012 Wrike, Inc.

License: GNU GPL 3
"""

from ztc.java.tomcat import TomcatJMXProxy

t = TomcatJMXProxy()
m = t.args[0]
t.get(m, *t.args[1:])
