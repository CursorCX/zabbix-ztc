#!/usr/bin/env python
# pylint: disable=F0401
"""
MySQL module for ZTC

Copyright (c) 2010-2011 Vladimir Rusinov <vladimir@greenmice.info>
Copyright (c) 2011 Murano Software [http://muranosoft.com]
Licensed under GNU GPL v.3
"""

import time

import MySQLdb

#import ztc.commons
from ztc.check import ZTCCheck, CheckFail


class MyDB(ZTCCheck):
    name = 'mysql'

    OPTPARSE_MIN_NUMBER_OF_ARGS = 1
    OPTPARSE_MAX_NUMBER_OF_ARGS = 2

    conn = None  # database connections
    cursor = None  # database cursor

    lasterr = None
    connected = None

    #def __init__(self):
    #    self.config = ztc.commons.get_config('mysql')
    #    self.database = self.config.get('database', self.database)
    #    self.host = self.config.get('host', self.host)
    #    self.user = self.config.get('user', self.user)
    #    self.password = self.config.get('password', self.password)
    #    self.unix_socket = self.config.get('unix_socket', self.unix_socket)
    #
    #    self._connect()

    def _connect(self):
        if self.connected:
            return True
        unix_socket = self.config.get('unix_socket', None)
        host = self.config.get('host', 'localhost')
        user = self.config.get('user', 'root')
        database = self.config.get('database', 'mysql')
        password = self.config.get('password', '')
        try:
            # TODO: remove this if, filter arguments instead
            if unix_socket:
                self.conn = MySQLdb.connect(host=host,
                           user=user,
                           passwd=password,
                           db=database,
                           unix_socket=unix_socket,
                           connect_timeout=2)
            else:
                self.conn = MySQLdb.connect(host=host,
                           user=user,
                           passwd=password,
                           db=database,
                           connect_timeout=2)
            self.cursor = self.conn.cursor()
            return True
        except MySQLdb.OperationalError:
            self.logger.error("Failed to connect to mysql")
            self.conn = None
            self.cursor = None
            return False

    def _get(self, metric, *args, **kwargs):
        if metric == 'ping':
            return self._get_ping()
        elif metric == 'status':
            try:
                return self._get_status(args[0])
            except IndexError:
                raise CheckFail("not enough arguments - pass global status "
                                "metric name as 2nd arg")

    def _get_ping(self):
        """ calculate ping by executing very simple select """
        st = time.time()
        if not self._connect():
            return 0
        else:
            self.query('SELECT 1')
            return time.time() - st

    def _get_status(self, metric):
        if not self._connect():
            self.logger.error("get_status: could not connect to mysql")
            # pylint: disable=E0702
            raise self.lasterr
        r = self.query('SHOW GLOBAL STATUS LIKE "%s"' % (self.escape(metric)))
        if r:
            return r[0][1]
        else:
            raise CheckFail('uncknown global status metric: %s' % (metric))

    def query(self, query):
        """ execute query and return all its results (fetchall) """
        self.logger.debug("running query '%s'" % (query,))
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def escape(self, s):
        return MySQLdb.escape_string(s)

if __name__ == '__main__':
    m = MyDB()
    print m.query("SELECT 1")
