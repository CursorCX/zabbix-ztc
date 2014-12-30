#!/usr/bin/env python
"""Tomcat jmx_proxy monitpring class

Copyright (c) 2012 Wrike. Inc.
Copyright (c) 2012 Vladimir Rusinov <vladimir@greenmice.info>
"""

import urllib2

from ztc.check import ZTCCheck


class TomcatJMXProxy(ZTCCheck):
    """ tomcat jmx_proxy monitoring class
    For more docs see
    http://tomcat.apache.org/tomcat-7.0-doc/manager-howto.html """

    name = "tomcat_jmx_proxy"

    OPTPARSE_MAX_NUMBER_OF_ARGS = 3

    proto = 'http'
    host = 'localhost'
    port = 8080
    username = 'zabbix'
    password = 'zabbix'
    timeout = 10

    def _myinit(self):
        self.proto = self.config.get('proto', self.proto)
        self.host = self.config.get('host', self.host)
        self.port = int(self.config.get('port', self.port))
        self.username = self.config.get('username', self.username)
        self.password = self.config.get('password', self.password)

    # pylint: disable=W0613
    def _get(self, metric, *arg, **kwarg):
        if metric == 'get':
            bean = arg[0]
            attr = arg[1]
            if len(arg) > 2:
                key = arg[2]
            else:
                key = None
            return self.get_jmx_attr(bean, attr, key)
        elif metric == 'threads':
            m = arg[0]
            return self.get_threads(m)
        elif metric == 'memory':
            t = arg[0]
            m = arg[1]
            return self.get_memory(t, m)
        else:
            raise NotImplementedError("Metric %s is not implemented" % metric)

    def get_jmx_attr(self, bean_name, attr, key=None):
        url = "%s://%s:%s/manager/jmxproxy/?get=%s&att=%s" % (
            self.proto,
            self.host,
            self.port,
            bean_name,
            attr)
        if key:
            url = url + "&key=%s" % key

        self.logger.debug("Fetching from %s" % url)

        # get the page
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, url, self.username, self.password)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        response = opener.open(url, None, self.timeout)
        resp_text = response.read().strip()
        self.logger.debug('got resp_text=%s' % resp_text)
        # pylint: disable=W0612
        (status, req, resp) = resp_text.split('-')  # @UnusedVariable
        if status.strip().lower() != 'ok':
            self.logger.error('Response is not ok')
            return None
        contents = resp.split('contents=')[-1].strip()
        if contents[-1] == ')':
            contents = contents[:-1]
        self.logger.debug('got contents=%s' % contents)
        return contents

    def _parse_java_dict(self, s):
        """ parse dict from s.
        Example:
        {committed=24576000, init=24313856, max=224395264, used=19720328} ->
        {
            'committed': '24576000',
            'init': '24313856',
            'max': '224395264',
            'used': '19720328',
        }
        """
        ret = {}
        if not (s.startswith('{') and s.endswith('}')):
            raise ValueError("Invalid dict format: '%s'" % s)
        s = s[1:-1]
        items = s.split(", ")
        for i in items:
            (key, value) = i.split('=')
            ret[key] = value
        return ret

    def get_threads(self, m):
        """ threads monitoring:
        bean: java.lang:type=Threading

        props
        * PeakThreadCount: 244
        * DaemonThreadCount: 105
        * ThreadCount: 244
        * TotalStartedThreadCount: 295
        * CurrentThreadCpuTime: 810000000
        * CurrentThreadUserTime: 780000000 """
        r = self.get_jmx_attr('java.lang:type=Threading', m)
        return int(r.split('=')[-1].strip())

    def get_memory(self, t, m):
        if t == 'heap':
            k = 'HeapMemoryUsage'
        elif t == 'nonheap':
            k = 'NonHeapMemoryUsage'
        else:
            raise NotImplementedError(
                                "metrics for memory %s is not supported" % t)

        r = self.get_jmx_attr('java.lang:type=Memory', k)
        return self._parse_java_dict(r)[m]
