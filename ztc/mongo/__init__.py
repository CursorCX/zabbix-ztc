#!/usr/bin/env python
"""
ZTC Mongodb check class

Copyright (c) 2011 Vladimir Rusinov <vladimir@greenmice.info>

Inspired by:
* http://blog.boxedice.com/2011/03/14/mongodb-monitoring-current-operations/
"""

import pymongo
import time

from ztc.check import ZTCCheck, CheckFail
from ztc.store import ZTCStore


class Mongo(ZTCCheck):
    name = "mongo"

    OPTPARSE_MAX_NUMBER_OF_ARGS = 3

    connection = None
    db = None
    dbs = {}

    def _connect(self):
        """ connect to mongodb """
        if not self.connection:
            host = self.config.get('host', 'localhost')
            port = int(self.config.get('port', 27017))
            db = self.config.get('db', 'ztc')
            self.connection = pymongo.Connection(host, port)
            self.db = self.connection[db]
            self.dbs[db] = self.db

    def _get(self, metric, *args):
        if metric == 'ping':
            return self.get_ping()
        elif metric == 'operations':
            m = args[0]
            return self.get_operations(m)
        elif metric == 'connections':
            m = args[0]
            return self.get_connections(m)
        elif metric == 'globallock':
            m = args[0]
            return self.get_globallock(m)
        elif metric == 'globallock_currentqueue':
            m = args[0]
            return self.get_globallock_currentqueue(m)
        elif metric == 'globallock_activeclients':
            m = args[0]
            return self.get_globallock_activeclients(m)
        elif metric == 'bgflushing':
            m = args[0]
            return self.get_bgflushing(m)
        elif metric == 'mem':
            m = args[0]
            return self.get_mem(m)
        elif metric == 'dbstats':
            # per-db metrics
            m = args[0]
            db = args[1]
            return self.get_dbstats(db, m)
        elif metric == 'page_faults':
            return self.get_page_faults()
        else:
            raise CheckFail("uncknown metric: %s" % metric)

    def get_ping(self):
        """ get ping to mongo db - time required to make a connection and
        execute simple query.
        Returns:
            float - number of seconds required to do a query
            0 - if mongodb failed
        """
        self.connection = None
        st = time.time()
        try:
            self._connect()
            #print dir(self.db)
            #print dir(self.connection)
            info = self.connection.server_info()
            if info and 'ok' in info:
                return time.time() - st
        except pymongo.errors.AutoReconnect:  # @UndefinedVariable
            self.logger.exception("failed to connect to mongodb")
        return 0

    def get_operations(self, m):
        """ get number of operations in specified state """
        self._connect()
        if m == 'all':
            ops = self.db['$cmd.sys.inprog'].find_one()
            r = 0
            for k in ops:
                r += len(ops[k])
            return r
        elif m == 'inprog':
            ops = self.db['$cmd.sys.inprog'].find_one()
            return len(ops['inprog'])

    def get_globallock(self, m):
        """ return globallock-related metrics:
        serverStatus().globalLock.$m """
        st = self.get_serverstatus()
        ret = st['globalLock'][m]
        if m in ('totalTime', 'lockTime'):
            ret = ret / 1000000.0
        return ret

    def get_globallock_currentqueue(self, m):
        """ return globallock currentQueue related metrics """
        cq = self.get_globallock('currentQueue')
        return cq[m]

    def get_globallock_activeclients(self, m):
        """ return globallock currentQueue related metrics """
        cq = self.get_globallock('activeClients')
        return cq[m]

    def get_serverstatus(self):
        """ returns output of serverstatus command (json parsed) """
        self._connect()
        ret = self.db.command('serverStatus')
        return ret

    def get_dbstats(self, dbname, metric):
        """ get db.stats metric for specified database """
        self._connect()
        # get database object
        if dbname not in self.dbs:
            self.dbs[dbname] = self.connection[dbname]
        db = self.dbs[dbname]

        # load dbstats for specified database
        c = ZTCStore('mongodb_dbstats_' + dbname, self.options, 120)
        dbstats = c.get()
        if not dbstats:
            dbstats = db.command('dbstats')
            c.set(dbstats)

        ret = dbstats[metric]
        if metric == 'nsSizeMB':
            ret = ret * 1024 * 1024
        return ret

    def get_bgflushing(self, m):
        """ return BackgroundFlushing metrics """
        st = self.get_serverstatus()
        ret = st['backgroundFlushing'][m]
        return ret

    def get_page_faults(self):
        """ return number of disk faults """
        st = self.get_serverstatus()
        ret = st['extra_info']['page_faults']
        return ret

    def get_mem(self, m):
        """ get memory metrics from db.serverStatus() """
        data = self.get_serverstatus()['mem']
        if m in ('resident', 'virtual', 'mapped', 'mappedWithJournal'):
            ret = data[m] * 1024 * 1204
        else:
            ret = data[m]
        return ret

    def get_connections(self, m):
        """ get number of from db.serverStatus() """
        data = self.get_serverstatus()['connections']
        return data[m]
