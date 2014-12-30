#!/usr/bin/env python
# pylint: disable = W0613
"""
<description>

This file is part of ZTC and distributed under the same license.
http://bitbucket.org/rvs/ztc/

Copyright (c) 2011 Vladimir Rusinov <vladimir@greenmice.info>
"""

import time
import os
import re
import urllib2

from ztc.check import ZTCCheck, CheckFail
import ztc.lib.flup_fcgi_client as fcgi_client
from ztc.store import ZTCStore


class PHPFPMCheck(ZTCCheck):
    """ PHP FPM (FastCGI Process Manager) check class """
    name = "php-fpm"

    OPTPARSE_MIN_NUMBER_OF_ARGS = 1
    OPTPARSE_MAX_NUMBER_OF_ARGS = 2

    _err_new_status = {} # record php-fpm log new error status
    _err_old_status = {} # record php-fpm log old error status

    _slow_new_status = {} # record php-fpm log slow new status
    _slow_old_status = {} # record php-fpm log slow old status

    _lines_err_record = ""
    _lines_slow_record = ""

    def _myinit(self):
        self.fcgi_port = self.config.get('fpm_port', 9000)
        self.fcgi_host = self.config.get('fpm_host', '127.0.0.1')

    def _get(self, metric, *arg, **kwarg):
        if metric == 'ping':
            return self.ping
        elif metric == 'status':
            m = arg[0]
            return self.get_status(m)
        elif metric == 'error':
            return self.get_err_count()
        elif metric == 'slow':
            return self.get_slow_count()
        else:
            raise CheckFail("uncknown metric")

    def _load_page(self, resource):
        """ load fastcgi page """
        try:
            url = "%s://%s%s" % (
                        self.config.get('proto', 'http'),
                        self.config.get('host','localhost'),
                        resource
                    )
            try:
                u = urllib2.urlopen(url, None, 1)
            except TypeError:
                u = urllib2.urlopen(url, None)
            out = {}
            for l in ''.join(u.readlines()).split('\n'):
                if len(l) > 1:
                    out[l.split(':')[0].strip()] = l.split(':')[1].strip()

            ret = (u.code, out)
            return ret
        except urllib2.URLError:
            self.logger.exception('fastcgi load fpm page')
            return False

    def _read_log_error(self):
        st = ZTCStore('php-fpm.record_log_error', self.options)
        #st.clear()
        self._err_old_status = st.get()
        if self._err_old_status == None:
            self._err_old_status = {}
        try:
            for f in self.config.get('err_log', '/var/log/php5-fpm.log').split(','):
                log_f = open(f, 'r')
                if self._err_old_status.has_key(f):
                    _offset = self._err_old_status[f]
                    if os.fstat(log_f.fileno()).st_size >= _offset:
                        log_f.seek(self._err_old_status[f])
                    else:
                        log_f.seek(0)
                    self._lines_err_record += ''.join(log_f.readlines())
                else:
                    self._lines_err_record += ''.join(log_f.readlines())

                _position = log_f.tell()
                self._err_new_status[f] = _position
                log_f.close()

            st.set(self._err_new_status)
            return True
        except IOError as ioerr:
            self.logger.exception('failed to open nginx access log')
            return False
        except Exception as err:
            self.logger.exception('unkowon error')
            return False

    def _read_log_slow(self):
        st = ZTCStore('php-fpm.record_log_slow', self.options)
        #st.clear()
        self._slow_old_status = st.get()
        if self._slow_old_status == None:
            self._slow_old_status = {}
        try:
            for f in self.config.get('slow_log', '/var/log/php5-fpm.log').split(','):
                log_f = open(f, 'r')
                if self._slow_old_status.has_key(f):
                    _offset = self._slow_old_status[f]
                    if os.fstat(log_f.fileno()).st_size >= _offset:
                        log_f.seek(self._slow_old_status[f])
                    else:
                        log_f.seek(0)
                    self._lines_slow_record += ''.join(log_f.readlines())
                else:
                    self._lines_slow_record += ''.join(log_f.readlines())

                _position = log_f.tell()
                self._slow_new_status[f] = _position
                log_f.close()

            st.set(self._slow_new_status)
            return True
        except IOError as ioerr:
            self.logger.exception('failed to open nginx access log')
            return False
        except Exception as err:
            self.logger.exception('unkowon error')
            return False

    def _slow_status_delta(self):
        _count = 0
        for l in self._lines_slow_record.split('\n'):
            if re.match(r"^\[.*\]",l) and not l.startswith('[0x'):
                _count += 1
        return _count

    def _err_status_delta(self):
        _count = 0
        for l in self._lines_err_record.split('\n'):
            if re.match(r"^\[.*\]",l):
                _count += 1
        return _count

    @property
    def ping(self):
        """ calls php-fpm ping resource """
        st = time.time()
        code, headers, out, err = self._load_page('/ping')  # @UnusedVariable
        if code.startswith('200') and out == 'pong':
            return time.time() - st
        else:
            self.logger.error('ping: got response, but not correct')
            return 0

    def get_slow_count(self):
        self._read_log_slow()
        if self._lines_slow_record:
            return self._slow_status_delta()
        else:
            return 0
    log_err = property(get_slow_count)

    def get_err_count(self):
        self._read_log_error()
        if self._lines_err_record:
            return self._err_status_delta()
        else:
            return 0
    log_err = property(get_err_count)

    def get_status(self, metric):
        """ get php-fpm status metric """
        metric = metric.replace('_', ' ')

        page = self.get_status_page()
        if not page:
            raise CheckFail("unable to get status page")
        if page.has_key(metric):
            return page[metric]
        # no such metric found
        raise CheckFail("no such metric found")

    def get_status_page(self):
        """ return php-ftm status page text """
        code, out = self._load_page('/fpm_status')  # @UnusedVariable
        if code == 200:
            return out
        else:
            self.logger.error('ping: got response, but not correct')
            return None

if __name__ == '__main__':
    st = PHPFPMCheck()
    print "fpm-status:", st.get_status('active_processes')
    #print "err_log:", st.get_err_count()
    #print "slow_log:", st.get_slow_count()
