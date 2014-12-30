#!/usr/bin/python
'''
MySQL script for ztc (mysql.ping item)
Connects to db and executes trivial query

Copyright (c) 2009-2011 Vladimir Rusinov <vladimir@greenmice.info>
License: GNU GPL3

This file is part of ZTC

Currently supported metrics:
    * ping (float) - return number of seconds required to run simple query.
        Return 0 if failed
    * status (mostly int) - returns value of $2 metric from mysql's SHOW GLOBAL
        STATUS
'''

from ztc.mysql import MyDB

my = MyDB()
m = my.args[0]
my.get(m, *my.args[1:])
