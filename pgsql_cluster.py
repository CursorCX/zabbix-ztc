#!/usr/bin/python
# pylint: disable=W0142
'''
Postgresql script for ztc (pgsql.* items)

Copyright (c) 2009-2011 Vladimir Rusinov <vladimir@greenmice.info>
Licensed under GNU GPL v.3
Currently supported metrics:
    * autovac_freeze (float) - returns max % of how close each database to
        autovac_freeze
'''

from ztc.pgsql.pgcluster import PgCluster

p = PgCluster()
m = p.args[0]
p.get(m, *p.args[1:])
