#!/usr/bin/env python
# pylint: disable-msg=W0232,W0201
'''
ZTC HTTP check class - used to query url

TODO: use this class on nginx and apache templates

Copyright (c) 2010-2011 Vladimir Rusinov <vladimir@greenmice.info>

Licensed under GPL v.3
'''

import urllib2
import socket
import time

from ztc.check import ZTCCheck, CheckFail


class HTTP(ZTCCheck):
    """ http checks class """
    name = 'net'

    OPTPARSE_MAX_NUMBER_OF_ARGS = 2

    def _get(self, metric, *arg):
        """ Return requested metric """
        if metric == 'ping':
            url = arg[0]
            return self.get_ping(url)
        else:
            raise CheckFail("unknown metric: %s" % metric)

    def _myinit(self):
        """ Constructor """
        self.timeout = self.config.get('timeout', 2)

    def get_ping(self, url):
        """ Calculate time required to fetch requested resource

        Params:
            url: string - full url of the resource to fetch, e.g.
                http://www.google.com/
        Returns:
            float: time in seconds spend fetching resource
        """
        start_time = time.time()
        try:
            urllib2.urlopen(url, None, self.timeout)
        except TypeError:
            # Changed in version 2.6: timeout was added, versions < 2.6 does
            # not have last param
            urllib2.urlopen(url, None)
        except socket.timeout:
            #if timeout, return 0 (same behaviour as net.tcp.service.perf)
            return 0
        return time.time() - start_time
