#!/usr/bin/python
# pylint: disable=W0142
'''
Mongodb script for ztc (mongo.* items)

Copyright (c) 2011 Vladimir Rusinov <vladimir@greenmice.info>

License: GNU GPL v.3
'''

from ztc.mongo import Mongo

d = Mongo()
m = d.args[0]
d.get(m, *d.args[1:])
