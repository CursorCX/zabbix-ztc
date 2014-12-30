#!/usr/bin/env python
#coding=utf-8
#pylint: disable=W0232
"""
ztc.nginx package

Copyright (c) 2010 Vladimir Rusinov <vladimir@greenmice.info>
License: GPL3
This file is part of ZTC [http://bitbucket.org/rvs/ztc/]
"""

import urllib2
import time
import os

#import ztc.commons
from ztc.check import ZTCCheck, CheckFail
from ztc.store import ZTCStore


class NginxStatus(ZTCCheck):
    """ Nginx status page reader and parser """

    OPTPARSE_MIN_NUMBER_OF_ARGS = 1
    OPTPARSE_MAX_NUMBER_OF_ARGS = 1
    name = 'nginx'

    _page_data = None  # data from status page
    _http_new_status = {} # http new status data from status page
    _http_old_status = {} # http old status data from status page
    _lines_record = "" # http data record
    ping_time = 0

    #pylint: disable=W0613
    def _get(self, metric=None, *args, **kwargs):
        """ get metric """
        allowed_metrics = ('accepts', 'handled', 'requests',
            'connections_active', 'connections_reading', 'connections_waiting',
            'connections_writing', 'ping', '2xx', '3xx', '4xx', '5xx')
        if metric in allowed_metrics:
            return self.__getattribute__('get_' + metric)()
        else:
            raise CheckFail("Requested not allowed metric")

    def _read_status(self):
        """ urlopen and save to _page_data text of status page """
        if self._page_data is not None:
            # we've already retrieved it
            return True

        st = ZTCStore('nginx.status_page', self.options)
        try:
            read_start = time.time()
            url = "%s://%s:%s%s?auto" % (
                                         self.config.get('proto', 'http'),
                                         self.config.get('host', 'localhost'),
                                         self.config.get('port', '8080'),
                                         self.config.get('resource',
                                                         '/server-status'))
            try:
                u = urllib2.urlopen(url, None, 1)
            except TypeError:
                u = urllib2.urlopen(url, None)
            self._page_data = u.readlines()
            u.close()
            st.set(self._page_data)
            # calulate how many time was required:
            self.ping_time = time.time() - read_start
            return True
        except urllib2.URLError:
            self.logger.exception('failed to load test page')
            # status page read failed
            self._page_data = st.get()
            self.ping_time = 0  # status page read failed
            return False

    def _read_http_status(self):
        st = ZTCStore('nginx.http_status_page', self.options)
        # store dict, ex. dict = { file:offset }
        # get old http status
        self._http_old_status = st.get()
        if self._http_old_status == None:
            self._http_old_status = {}
        try:
            for f in self.config.get('logfile', '/var/log/nginx/access.log').split(','):
                log_f = open(f,'r')
                if self._http_old_status.has_key(f):
                    # get _offset value
                    _offset = self._http_old_status[f]
                    # comp file size and _offset
                    if os.fstat(log_f.fileno()).st_size >= _offset:
                        # 当前文件size大于offset
                        log_f.seek(self._http_old_status[f])
                    else:
                        # 当日志清空或被切割时,当前size小于offset
                        log_f.seek(0)
                    self._lines_record += ''.join(log_f.readlines())
                else:
                    self._lines_record += ''.join(log_f.readlines())

                # 得到当前文件的偏移位
                _position = log_f.tell()
                self._http_new_status[f] = _position
                log_f.close()

            st.set(self._http_new_status)
            return True
        except IOError as ioerr:
            self.logger.exception('failed to open nginx access log')
            return False
        except Exception as err:
            self.logger.exception('unkowon error')
            return False

    def _get_info(self, name):
        """ Extracts info from status """
        self._read_status()
        ret = None
        for l in self._page_data.split("\n"):
            if l.find(name + ": ") == 0:
                ret = l.split()[-1]
                break
        return ret

    def _http_status_delta(self, type):
        """ Calculate http staus delta """
        _count = 0
        #print self._lines_record
        for l in self._lines_record.split('\n'):
            if len(l.split('')) > 6:
                t_status = l.split('')[6].strip()
                if t_status[:1] == type[:1]:
                    _count += 1
            else:
                continue
        return _count

    def get_2xx(self):
        """ Number of 2xx delta state """
        self._read_http_status()
        if self._lines_record:
            return self._http_status_delta("2xx")
        else:
            return 0
    status_2xx = property(get_2xx)

    def get_3xx(self):
        """ Number of 3xx delta state """
        self._read_http_status()
        if self._http_new_status:
            return self._http_status_delta("3xx")
        else:
            return 0
    status_3xx = property(get_3xx)

    def get_4xx(self):
        """ Number of 4xx delta state """
        self._read_http_status()
        if self._http_new_status:
            return self._http_status_delta("4xx")
        else:
            return 0
    status_4xx = property(get_4xx)

    def get_5xx(self):
        """ Number of 5xx delta state """
        self._read_http_status()
        if self._http_new_status:
            return self._http_status_delta("5xx")
        else:
            return 0
    status_5xx = property(get_5xx)

    def get_accepts(self):
        """ Number of accept()s since server start """
        self._read_status()
        if self._page_data:
            my_line = self._page_data[2]
            return int(my_line.split()[0])
        else:
            return 0
    accepts = property(get_accepts)

    def get_handled(self):
        """ Number of handled()s since server start """
        self._read_status()
        if self._page_data:
            my_line = self._page_data[2]
            return int(my_line.split()[1])
        else:
            # no data neither in nginx or cache
            return 0
    handled = property(get_handled)

    def get_requests(self):
        """ Number of requests()s since server start """
        self._read_status()
        if self._page_data:
            my_line = self._page_data[2]
            return int(my_line.split()[2])
        else:
            return 0
    requests = property(get_requests)

    def get_connections_active(self):
        """
        first line:
        Active connections: 123
        """
        try:
            self._read_status()
            my = self._page_data[0].split()[-1]
            return int(my)
        except:
            return 0
    connections_active = property(get_connections_active)

    def get_connections_reading(self):
        try:
            self._read_status()
            my = self._page_data[-1].split()[1]
            return int(my)
        except:
            return 0
    connections_reading = property(get_connections_reading)

    def get_connections_waiting(self):
        try:
            self._read_status()
            my = self._page_data[-1].split()[5]
            return int(my)
        except:
            return 0
    connections_waiting = property(get_connections_waiting)

    def get_connections_writing(self):
        try:
            self._read_status()
            my = self._page_data[-1].split()[3]
            return int(my)
        except:
            return 0
    connections_writing = property(get_connections_writing)

    def get_ping(self):
        try:
            self._read_status()
        finally:
            return self.ping_time
    ping = property(get_ping)


if __name__ == '__main__':
    st = NginxStatus()
    print "2xx:", st.get_2xx()
