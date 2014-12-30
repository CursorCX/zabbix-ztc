#!/usr/bin/env python
"""
ZTC Ldap check

Copyright (c) 2012 Vladimir Rusinov <vladimir@greenmice.info>

This file is part of ZTC and distributed under the same license.

Requirements:
    * python-ldap
"""

import time

import ldap

from ztc.check import ZTCCheck


class LDAPCheck(ZTCCheck):
    name = "ldap"

    def _get(self, metric, *arg, **kwarg):
        if metric == 'ping':
            return self.ping()

    def _connect(self):
        """ connect to ldap server """
        self.con = ldap.initialize(self.config.get('ldap_url',
                                                   'ldap://localhost'))
        self.con.simple_bind_s()

    def ping(self):
        """ping ldap server - execute simple query and calculate time
        required"""
        st = time.time()
        try:
            self._connect()
            ret = time.time() - st
            return ret
        except ldap.SERVER_DOWN:
            self.logger.exception('ldap server is down')
        except:
            self.logger.exception('uncknown error')
        return 0

if __name__ == '__main__':
    c = LDAPCheck()
    print c.ping()
