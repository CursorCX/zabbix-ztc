#!/usr/bin/env python
"""
PgDB class - ZTCCheck for tracking single postgresql database

Copyright (c) 2012 Wrike, Inc. [http://www.wrike.com]

Requirements:
    * permissions to execute pg_controldata on $PGDATA
"""

import time

from ztc.check import ZTCCheck, CheckFail
import ztc.myos


class PgControldata(ZTCCheck):
    """ pg_controldata related checks """

    name = 'pgsql'

    OPTPARSE_MIN_NUMBER_OF_ARGS = 1
    OPTPARSE_MAX_NUMBER_OF_ARGS = 1

    def _get(self, metric, *args, **kwargs):
        if metric == 'last_checkpoint_age':
            return self.get_last_checkpoint_age()
        else:
            raise CheckFail('uncknown metric %s' % metric)

    def get_last_checkpoint_age(self):
        """ return age of last checkpoint """
        pgdir = self.config.get('pgdata', '/var/lib/pgsql/data')
        pg_controldata = self.config.get('pg_controldata', 'pg_controldata')

        cmd = "%s %s" % (pg_controldata, pgdir)
        code, ret = ztc.myos.popen(cmd, self.logger)
        date_str = ''
        if code != 0:
            self.logger.error('pg_controldata returned non-zero')
            raise CheckFail('error executing pg_controldata')
        for line in ret.splitlines():
            if line.startswith('Time of latest checkpoint:'):
                date_str = line.split(':', 1)[1].strip()
                self.logger.debug('Got date %s' % date_str)

        if not date_str:
            # no 'Time of latest checkpoint' found in pg_controldata output
            raise CheckFail("no 'Time of latest checkpoint' "
                            "info found in pg_controldata output")

        date = time.mktime(time.strptime(date_str))
        return time.time() - date

if __name__ == '__main__':
    pc = PgControldata()
    print pc.get_last_checkpoint_age()
