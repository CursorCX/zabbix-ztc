#!/usr/bin/python
'''
Copyright (c) 2009-2011 Vladimir Rusinov <vladimir@greenmice.info>
Copyright (c) 2012 Wrike, Inc. [http://www.wrike.com]

License: GNU GPL v.3
'''

from ztc.pgsql.pg_controldata import PgControldata

p = PgControldata()
m = p.args[0]
p.get(m, *p.args[1:])
