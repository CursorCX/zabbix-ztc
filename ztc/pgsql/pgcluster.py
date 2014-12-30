#!/usr/bin/env python
#pylint: disable-msg=W0232
"""PgCluster ZTCCheck
Used to perform database-wide checks (like querying each database of the
cluster)

Copyright (c) pg_check.pl authors
Copyright (c) 2010-2011 Vladimir Rusinov <vladimir@greenmice.info>
Copyright (c) 2011 Wrike, Inc. [http://www.wrike.com]
"""

import heapq

from ztc.check import ZTCCheck
from ztc.pgsql.pgconn import PgConn
import ztc.pgsql.queries as pgq


class PgCluster(ZTCCheck):
    """ Class represent database cluster """

    name = 'pgsql'

    OPTPARSE_MIN_NUMBER_OF_ARGS = 1

    dbs = []

    @property
    def bloat(self):
        """ get max database bloat of all databases of cluster """
        query = pgq.BLOAT
        pages = 0
        otta = 0
        bloatest = []  # list of bloatest tables
        ret = self.query_eachdb(query, exclude=['template0'])
        for db in ret.keys():  # pylint:disable-msg=C0103
            # loop through all databases
            for table in ret[db]:
                # and its tables
                pages += table[4]
                otta += table[5]
                if pages > 1000:
                    # add to list of bloatest tables
                    bloat = 100 - 100 * (pages - otta) / pages
                    item = (bloat, "%s.%s.%s->%s" % (db, table[0], table[1],
                                                     table[2]))
                    if len(bloatest) < 5:
                        heapq.heappush(bloatest, item)
                    else:
                        heapq.heapreplace(bloatest, item)
        self.logger.debug("pages: %i, otta: %i" % (pages, otta))

        # print out list of tables with higest bloat
        while len(bloatest):
            table = heapq.heappop(bloatest)
            self.logger.debug("bloatest: %s: %.2f%%" % (table[1],
                                                        100 - table[0]))
        if pages < 5000:  # cluster < then 40 Mb is no serious
            return 0
        else:
            return 100 * (pages - otta) / pages

    # lower-level functions
    def get_dblist(self):
        """ Get list of all databases

        Returns: list of strings - names of all databases of postgresql
            cluster
        """
        connect_dict = {
            'host': self.config.get('host', None),  # none = connect via socket
            'user': self.config.get('user', 'postgres'),
            'password': self.config.get('password', None),
            'database': self.config.get('database', 'postgres')}
        db = PgConn(connect_dict, self.logger)  # pylint: disable-msg=C0103
        dbs = db.query("SELECT datname FROM pg_database")
        self.dbs = [x[0] for x in dbs]

    def query_eachdb(self, sql, exclude=None):
        """ execure query on each database of the cluster
        Params:
            sql (string): query text
            exclude (list of strings): database names to exclude
        Out:
            { dbname: query_result, ...  }
        """

        connect_dict = {
            'host': self.config.get('host', None),  # none = connect via socket
            'user': self.config.get('user', 'postgres'),
            'password': self.config.get('password', None),
            'database': self.config.get('database', 'postgres')}

        ret = {}
        if not self.dbs:
            self.get_dblist()
        for db in self.dbs:  # pylint: disable-msg=C0103
            if db in exclude:
                continue
            connect_dict['database'] = db
            pdb = PgConn(connect_dict, self.logger)
            ret[db] = pdb.query(sql)
        return ret
