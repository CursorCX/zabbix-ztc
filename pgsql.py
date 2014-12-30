#!/usr/bin/python
'''
Postgresql script for ztc (pgsql.* items)

Copyright (c) 2009-2011 Vladimir Rusinov <vladimir@greenmice.info>

License: GNU GPL v.3

Currently supported metrics:
    * autovac_freeze (float) - returns max % of how close each database to
        autovac_freeze
    * ping (float) - returns time required to execute trivial query
    * tnxage running|idle_tnx (float) - maximum age (in seconds) of transaction
        in given state
'''

from ztc.pgsql.pgdb import PgDB

p = PgDB()
m = p.args[0]
p.get(m, *p.args[1:])
