#!/usr/bin/env python
"""
ztc.apache package
Used in ztc Apache template

Copyright (c) 2010-2012 Vladimir Rusinov <vladimir@greenmice.info>
Copyright (c) 2010 Murano Software [http://muranosoft.com/]
License: GNU GPL v.3
"""

import os
import time
import urllib2
import socket

from ztc.check import ZTCCheck, CheckFail
from ztc.store import ZTCStore


class ApacheStatus(ZTCCheck):
    """ Apache status page reader & parser """

    name = 'apache'

    OPTPARSE_MIN_NUMBER_OF_ARGS = 1
    OPTPARSE_MAX_NUMBER_OF_ARGS = 1

    ping_t = 0

    _page_data = None

    def _read_status(self):
        """ urlopen and save to _page_data text of status page """
        st = time.time()
        if self._page_data is not None:
            # we've already retrieved it
            return 1
        proto = self.config.get('proto', 'http')
        url = "%s://%s:%s%s?auto" % (
                                      proto,
                                      self.config.get('host', 'localhost'),
                                      self.config.get(
                                        'port',
                                        socket.getservbyname(proto, 'tcp')),
                                      self.config.get(
                                        'resource',
                                        '/server-status'))
        self.logger.debug("opening url %s" % url)
        try:
            u = urllib2.urlopen(url, None, 1)
        except TypeError:
            u = urllib2.urlopen(url, None)
        self._page_data = u.read()
        u.close()
        self.ping_t = time.time() - st

    def _get_info(self, name):
        """ Extracts info from status """
        self._read_status()
        self.logger.debug("Getting apache info metric %s" % name)
        ret = None
        for l in self._page_data.splitlines():
            self.logger.debug("_get_info: got line '%s'" % l)
            if l.startswith(name + ": "):
                ret = l.split()[-1]
                break
        return ret

    def get_scoreboard(self):
        """ Return apache workers scoreboard """
        ret = self._get_info('Scoreboard')
        self.logger.debug("get_scoreboard: %s" % (ret,))
        return ret

    def _get(self, metric=None, *args, **kwargs):
        """ get some metric """
        allowed_metrics = ('ping', 'accesses', 'bytes', 'workers_busy',
            'workers_closingconn', 'workers_dns', 'workers_finishing',
            'workers_idle', 'workers_idlecleanup', 'workers_keepalive',
            'workers_logging', 'workers_openslot', 'workers_reading',
            'workers_starting', 'workers_writing')
        if metric in allowed_metrics:
            return self.__getattribute__('get_' + metric)()
        else:
            raise CheckFail("Requested not allowed metric")

    ####################################################################
    ## Properties ######################################################

    def get_ping(self):
        """ Returns time required to load test page """
        try:
            self._read_status()
        # pylint: disable=W0702
        except:
            pass
        return self.ping_t

    def get_accesses(self):
        return int(self._get_info('Total Accesses'))
    accesses = property(get_accesses)

    @property
    def bytes(self):  # @ReservedAssignment
        return int(self._get_info('Total kBytes')) * 1024

    def get_workers_busy(self):
        return int(self._get_info('BusyWorkers'))
    workers_busy = property(get_workers_busy)

    def get_workers_idle(self):
        return int(self._get_info('IdleWorkers'))
    workers_idle = property(get_workers_idle)

    def get_workers_closingconn(self):
        return self.get_scoreboard().count('C')
    workers_closingconn = property(get_workers_closingconn)

    def get_workers_dns(self):
        return self.get_scoreboard().count('D')
    workers_dns = property(get_workers_dns)

    def get_workers_finishing(self):
        return self.get_scoreboard().count('G')
    workers_finishing = property(get_workers_finishing)

    def get_workers_idlecleanup(self):
        return self.get_scoreboard().count('I')
    workers_idlecleanup = property(get_workers_idlecleanup)

    def get_workers_keepalive(self):
        return self.get_scoreboard().count('K')
    workers_keepalive = property(get_workers_keepalive)

    def get_workers_logging(self):
        return self.get_scoreboard().count('L')
    workers_logging = property(get_workers_logging)

    def get_workers_openslot(self):
        return self.get_scoreboard().count('.')
    workers_openslot = property(get_workers_openslot)

    def get_workers_reading(self):
        return self.get_scoreboard().count('R')
    workers_reading = property(get_workers_reading)

    def get_workers_starting(self):
        return self.get_scoreboard().count('S')
    workers_starting = property(get_workers_starting)

    def get_workers_writing(self):
        return self.get_scoreboard().count('W')


class ApacheTimeLog(ZTCCheck):
    """ Processes Apache time log (LogFormat %D) """

    OPTPARSE_MAX_NUMBER_OF_ARGS = 1

    name = 'apache'
    log = None

    def _openlog(self):
        """ Open Log File and save it as self.log file object """
        logdir = self.config.get('logdir', '/var/log/apache2/')
        logfile = self.config.get('timelog', 'time.log')
        fn = os.path.join(logdir, logfile)
        self.log = open(fn, 'a+')

    def _closelog(self):
        self.log.close()

    def _truncatelog(self):
        self.log.truncate(0)

    def _get_metrics(self):
        """ Calculates average, max & min request processing time, in
        seconds """
        total_time = 0
        max_time = 0
        min_time = -1
        total_lines = 0
        self._openlog()
        ret = {'avg': 0, 'min': 0, 'max': 0}
        slowlog_time = int(self.config.get('slowlog', 0))
        slowlog_path = os.path.join(
            self.config.get('logdir', '/var/log/apache2/'),
            self.config.get('slowlog_file', 'slow.log'))
        for l in self.log.readlines():
            if not l.strip():
                # skip empty lines
                continue
            c_time = int(l.split()[0])
            total_time += c_time
            if max_time < c_time:
                max_time = c_time
            if min_time == -1 or min_time > c_time:
                min_time = c_time
            if slowlog_time and (c_time > slowlog_time):
                # log slow queries
                f = open(slowlog_path, 'a')
                f.write(str(int(c_time * 0.000001)) + ' ' + \
                        " ".join(l.split()[1:]) + "\n")
                f.close()
            total_lines += 1
        self._truncatelog()
        self._closelog()
        if total_lines != 0:
            ret = {
                   # convert to seconds
                   'avg': float(total_time) / total_lines * 0.000001,
                   'min': float(min_time) * 0.000001,
                   'max': float(max_time) * 0.000001,
                   }
        self._save_metrics_to_cache(ret)
        return ret

    def _get_metrics_from_cache(self):
        """ load page response metrics from ZTCStore key apache_reqtime """
        st = ZTCStore('apache_reqtime', self.options)
        return st.get()

    def _save_metrics_to_cache(self, data):
        st = ZTCStore('apache_reqtime', self.options)
        st.set(data)

    def _get(self, metric=None, *args, **kwargs):
        """ get some metric """
        if metric == 'avg':
            return self.get_avg()
        elif metric == 'min':
            return self.get_min()
        elif metric == 'max':
            return self.get_max()
        else:
            raise CheckFail("Uncknown metric: %s" % (metric,))

    def get_avg(self):
        """ returns average request processing time """
        metrics = self._get_metrics()
        return metrics['avg']

    def get_min(self):
        metrics = self._get_metrics_from_cache()
        return metrics['min']

    def get_max(self):
        metrics = self._get_metrics_from_cache()
        return metrics['max']
    max_request_time = property(get_max)
