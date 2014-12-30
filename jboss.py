#!/usr/bin/python
"""
jboss.* scripts item

Copyright (c) 2011 Vladimir Rusinov <vladimir@greenmice.info>
Copyright (c) 2001 Wrike, Inc. [http://www.wrike.com]
License: GNU GPL3
This file is part of ZTC [http://bitbucket.org/ztc/ztc/]

Example usage:
    ./jboss.py get_prop jboss.system:type=ServerInfo FreeMemory
"""

from ztc.java.jboss import JMXJboss

j = JMXJboss()
m = j.args[0]
j.get(m, *j.args[1:])
