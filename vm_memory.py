#!/usr/bin/python
"""
vm.memory.* scripts item


This file is part of ZTC and distributed under GNU GPL v.3
Copyright (c) 2010 Vladimir Rusinov <vladimir@greenmice.info>

Params:
    $1 - metric name. Supported:
        active - amount of active (recently accessed) memory
        inavtive - amount of inactive (not accessed recently) memory
"""

from ztc.vm.memory import Memory


c = Memory()
m = c.args[0]
c.get(m, *c.args[1:])
