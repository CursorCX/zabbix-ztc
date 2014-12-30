#!/usr/bin/env python
'''
Time monitoring class for ZTC

Copyright (c) 2010-2012 Vladimir Rusinov <vladimir@greenmice.info>
Copyright (c) 2010 Murano Software [http://muranosoft.com]
Copyright (c) 2010 Docufide, Inc. [http://docufide.com]
Copyright (c) 2011 Wrike, Inc. [http://www.wrike.com]
License: GNU GPL v3

Requirements:
 * ntpq
'''

import socket

import ntplib

from ztc.check import ZTCCheck


class DumbNtpResponse(object):
    """dumb ntp response - mock object on ntplib response object"""
    offset = 3600.0
    delay = 3600.0
    precision = 1


class TimeCheck(ZTCCheck):
    name = 'time'
    _ntp_response = None

    def _myinit(self):
        """__init__"""
        self._ntp_addr = self.config.get('ntp_server', 'pool.ntp.org')

        # default timeout is 1 second
        self._timeout = self.config.get('timeout', 1)

    def _get(self, metric, *args, **kwargs):
        """Get some ntp mertic. Howewer, only jitter is currently supported"""
        return self.__getattribute__(metric)

    def _read_ntp(self):
        """Connect to ntp server and read vars from it
        Returns: ntplib response object"""
        if self._ntp_response:
            return self._ntp_response

        try:
            self.logger.debug("connecting to ntp server %s" % self._ntp_addr)
            c = ntplib.NTPClient()
            # TODO: add timeout param
            response = c.request(self._ntp_addr, version=3)
            self._ntp_response = response
        except socket.timeout:
            self.logger.exception("Failed to read from ntp server")
            response = DumbNtpResponse()
        self._ntp_response = response
        return response

    @property
    def offset(self):
        response = self._read_ntp()
        return abs(response.offset)

    @property
    def delay(self):
        response = self._read_ntp()
        return abs(response.delay)

    @property
    def precision(self):
        response = self._read_ntp()
        return abs(2 ** response.precision)
