#!/usr/bin/env python
#pylint: disable-msg=W0232
"""
Nginx Status Log check class: calculates number of responses in given status
(since last run)

Usage:
1. configure status_log log format in nginx config (http section):
log_format status_log '$status <anything you want additionaly>';

2. Add statuslog log to all servers/locations you need to monitor:
access_log /var/log/nginx/status.log status_log;

3. Check log path on config file /etc/ztc/nginx.conf

4. Make sure zabbix can execute nginx_reqtime.py script under root (to allow
cleaning of the log)

5. It might be good idea to place this log to tmpfs.

This file is part of ZTC and distributed under the same license.
http://bitbucket.org/rvs/ztc/

Copyright (c) 2011-2012 Vladimir Rusinov <vladimir@greenmice.info>
"""

from ztc.check import ZTCCheck, CheckFail
from ztc.store import ZTCStore


class NginxStatusLog(ZTCCheck):
    """ Nginx upsteam response min/avg/max calculation """
    name = 'nginx'

    OPTPARSE_MIN_NUMBER_OF_ARGS = 2
    OPTPARSE_MAX_NUMBER_OF_ARGS = 2

    #pylint: disable-msg=W0613
    def _get(self, metric=None, *args, **kwargs):
        """ get metric """
        if metric == 'num':
            status = args[0]
            return self.get_status_num(status)
        else:
            CheckFail('uncknown metric %s' % metric)

    def get_status_num(self, status):
        """ get number of requests returned given status """
        st = None
        if status != '200':
            # read from store for non-200 statues
            st = self.read_from_store()
        if not st:
            st = self.read_statuslog()
            self.save_to_store(st)

        k = int(status)
        if k in st:
            return st[k]
        else:
            return 0

    def read_statuslog(self):
        """ really open timelog and calculate data """
        statuses = {}

        fn = self.config.get('statuslog', '/var/log/nginx/status.log')
        f = open(fn, 'a+')

        for l in f.readlines():
            st = l.split()[0]  # response time should be in first col
            st = int(st)
            if st in statuses:
                statuses[st] += 1
            else:
                statuses[st] = 1

        f.truncate(0)
        f.close()

        return statuses

    def save_to_store(self, data):
        """ Save fetched status to ZTCStore cache. """ 
        st = ZTCStore('nginx_statuses', self.options)
        st.set(data)

    def read_from_store(self):
        """ Read from ZTCStore cache """
        st = ZTCStore('nginx_statuses', self.options)
        return st.get()
