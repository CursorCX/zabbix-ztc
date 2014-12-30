#!/usr/bin/env python
"""
PgDB class - ZTCCheck for tracking single postgresql database

Copyright (c) 2010-2011 Vladimir Rusinov <vladimir@greenmice.info>

Requirements:
    * PostgreSQL 8.3 or older
    * pg_buffercache from contrib installed on configured db/user
"""

import time
import re

from ztc.check import ZTCCheck, CheckFail
import ztc.pgsql.queries as pgq
from ztc.pgsql.pgconn import PgConn


class PgDB(ZTCCheck):
    """ Connection to single database """

    name = 'pgsql'
    dbconn = None

    OPTPARSE_MIN_NUMBER_OF_ARGS = 1
    OPTPARSE_MAX_NUMBER_OF_ARGS = 3

    def _myinit(self):
        connect_dict = {
            'host': self.config.get('host', None),  # none = connect via socket
            'user': self.config.get('user', 'postgres'),
            'password': self.config.get('password', None),
            'database': self.config.get('database', 'postgres')}
        self.dbconn = PgConn(connect_dict, self.logger)

    def _get(self, metric, *args, **kwargs):
        if metric == 'query':
            q = args[0]
            return self.dbconn.query(q)
        elif metric == 'autovac_freeze':
            return self.get_autovac_freeze()
        elif metric == 'ping':
            return self.get_ping()
        elif metric == 'tnxage':
            state = args[0]
            return self.get_tnx_age(state)
        elif metric == 'buffers':
            buf_metric = args[0]
            return self.get_buffers(buf_metric)
        elif metric == 'conn':
            state = args[0]
            return self.get_conn_nr(state)
        elif metric == 'dbstat':
            m = args[0]
            return self.get_dbstat(m)
        elif metric == 'fsm':
            m = args[0]
            return self.get_fsm(m)
        elif metric == 'locks':
            m = args[0]
            mm = args[1]
            return self.get_locks(m, mm)
        elif metric == 'bgwriter':
            bgw_metric = args[0]
            return self.get_bgwriter(bgw_metric)
        elif metric == 'settings':
            param = args[0]
            return self.get_setting(param)
        elif metric == 'wal':
            m = args[0]
            if m == 'num':
                return self.get_wal_num()
            else:
                CheckFail('uncknown wal metric: %s' % m)
        else:
            raise CheckFail('uncknown metric %s' % metric)

    def get_fsm(self, metric):
        """ PostgreSQL freespacemap metrics.
        Requirements: pg_freespacement, PostgreSQL <= 8.3"""
        q = pgq.FSM[metric]
        ret = self.dbconn.query(q)[0][0]
        return ret

    def get_buffers(self, metric):
        """ PostgreSQL buffer metrics: number of clear/dirty/used/total buffers.
        Requirements: pg_buffercache contrib """
        q = pgq.BUFFER[metric]
        ret = self.dbconn.query(q)[0][0]
        return ret

    def get_dbstat(self, m):
        """ get sum of passed metric from dbstat """
        q = "SELECT SUM(%s) FROM pg_stat_database" % m
        ret = self.dbconn.query(q)[0][0]
        return ret

    def get_conn_nr(self, state):
        """ Get number of connections in given state """
        v = self._get_version()
        if v >= (9, 2, 0):
            vtag = 'post92'
        else:
            vtag = 'pre92'

        # we don't need to be able to read queries to get total and max
        if state!='total':
            q = pgq.CHECK_INSUFF_PRIV[vtag]
            insuff_priv = self.dbconn.query(q)
            if insuff_priv:
                raise CheckFail(
                    "Insufficient privileges to read queries from pg_stat_activity")
        try:
            q = pgq.CONN_NUMBER[vtag][state]
        except KeyError:
                raise CheckFail("Unknown connection state requested")

        ret = self.dbconn.query(q)[0][0]
        return ret

    def get_tnx_age(self, state):
        """ Get max age of transactions in given state.
        Supported states are: 'running', 'idle_tnx', 'prepared'
        """
        v = self._get_version()
        if v >= (9, 2, 0):
            vtag = 'post92'
        else:
            vtag = 'pre92'
        if state == 'prepared':
            q = pgq.TNX_AGE_PREPARED
        else:
            q = pgq.CHECK_INSUFF_PRIV[vtag]
            insuff_priv = self.dbconn.query(q)
            if insuff_priv:
                raise CheckFail(
                    "Insufficient privileges to read queries from pg_stat_activity")
            try:
                q = pgq.TNX_AGE[vtag][state]
            except KeyError:
                raise CheckFail("Unknown transaction state requested")

        # the query always returns something becuase of COALESCE(..., 0),
        # even if there's no transactions in given state
        ret = self.dbconn.query(q)[0][0]
        return abs(ret)

    def get_ping(self):
        """get amount of time required to execute trivial query"""
        st = time.time()
        try:
            if self.dbconn.query('SELECT 1'):
                return time.time() - st
            else:
                return 0
        except:
            return 0

    def get_autovac_freeze(self):
        """ Checks how close each database is to the Postgres
            autovacuum_freeze_max_age setting. This action will only work for
            databases version 8.2 or higher. The 'age' of the transactions in
            each database is compared to the autovacuum_freeze_max_age setting
            (200 million by default) to generate a rounded percentage.

        Returns: (float) maximum age of transaction from all databases, in %
            (compared to autovacuum_freeze_max_age)
        """
        max_percent = 0
        q = pgq.AUTOVAC_FREEZE
        ret = self.dbconn.query(q)
        for (freeze, age, percent, dbname) in ret:  # @UnusedVariable
            if self.debug:
                self.logger.info("Freeze %% for %s: %s" % (dbname, percent))
            max_percent = max(max_percent, percent)
        return max_percent

    def get_locks(self, m, mm=None):
        """ get number of database locks """
        if m == 'mode':
            q = pgq.LOCKS_BY_MODE[mm.lower()]
        else:
            q = pgq.LOCKS[m]
        ret = self.dbconn.query(q)[0][0]
        return ret

    def get_wal_num(self):
        """ get number of wal files in pg_xlog directory """
        q = pgq.WAL_NUMBER
        ret = self.dbconn.query(q)[0][0]
        return ret

    def get_bgwriter(self, m):
        """ Get stats for bgwriter. Currently used metrics are:
        'checkpoints_timed', 'checkpoints_req',
        'buffers_checkpoint', 'buffers_clean', 'maxwritten_clean',
        'buffers_backend', 'buffers_alloc' """
        q = "select %s from pg_stat_bgwriter" % m
        ret = self.dbconn.query(q)[0][0]
        return ret

    def _get_version(self):
        """ Get postgresql version. Result returned as (x,y,z) tuple, each member
            of which is an integer. Functions returns (0,0,0) if fails to obtain
            or parse version string.
        """
        dummy_version = (0, 0, 0)
        q = 'SELECT version()'
        v_str = self.dbconn.query(q)[0][0]
        if not v_str:
            self.logger.warning("Failed to fetch version with query %s" % q)
            return dummy_version
        m = re.search(r'PostgreSQL (\d+)\.(\d+)\.(\d+).+', v_str)
        if not m:
            self.logger.warning("Failed to parse version string: %s" % v_str)
            return dummy_version
        # convert every element of resulting tuple to integer
        # there's no way it can cause ValueError, becuase search regexp matches
        # only digits.
        version = tuple(int(k) for k in m.groups())
        return version

    def get_setting(self, parameter):
        """ Get arbitrary postgresql user configurable parameter """
        q = pgq.GET_SETTING % (parameter)
        res = self.dbconn.query(q)
        if res:
            return res[0][0]
        raise CheckFail("The requested parameter %s does not exist in pg_settings" % parameter)
