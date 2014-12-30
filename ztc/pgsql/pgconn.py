#!/usr/bin/env python
#pylint: disable=W0142
"""
Helper pgsql connection class

Provides methods like connect, query and so on

Copyright (c) 2010-2011 Vladimir Rusinov <vladimir@greenmice.info>
"""

import psycopg2 as pg


class PgConn(object):
    dbh = None  # database handler
    cur = None  # database cursor

    def __init__(self, connect_dict, logger):
        self.logger = logger
        self._connect(connect_dict)
        self.lasterr = None

    def _connect(self, connect_dict):
        """ Connect to database """
        if self.dbh:
            return True

        # filtering connect_dict to remove all Nones:
        connect_dict = dict((k, v) for k, v in connect_dict.iteritems() \
                            if v is not None)
        self.logger.debug('db connection dict: %s' % connect_dict)
        try:
            self.dbh = pg.connect(**connect_dict)
            self.cur = self.dbh.cursor()
            return True
        # pylint: disable=W0703
        except  Exception, e:
            #raise
            self.logger.warn("Failed to connect to postgresql: %s" % e)
            self.lasterr = e
            self.dbh = None
            self.cur = None
            return False

    def query(self, sql):
        #self._connect()
        self.logger.debug("running query '%s'" % sql)
        if self.cur:
            self.cur.execute(sql)
            ret = self.cur.fetchall()
        else:
            self.logger.warn("Failed to query: not connected to database")
            ret = None
        #self.logger.debug("result:\n%s" % self.fineprint_results(ret))
        return ret

    def fineprint_results(self, rets):
        """ Fine print query results """
        ret = ''
        for row in rets:
            for cell in row:
                ret += (str(cell) + ' | ')
            ret += "\n"
        return ret

    def close(self):
        self.cur.close()
        self.dbh.close()
