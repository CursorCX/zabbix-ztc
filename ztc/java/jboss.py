#!/usr/bin/env python
"""
    Jboss check class for ZTC. Licensed under the same terms as ZTC.

    Copyright (c) 2011 Wrike, Inc. [http://www.wrike.com]
    Copyright (c) 2011 Vladimir Rusinov <vladimir@greenmice.info>

Use jboss-remoting.sar from server/all/deploy/ to enable remote jmx support
"""

from ztc.check import CheckFail
from ztc.java.jmx import JMXCheck


class JMXJboss(JMXCheck):
    """ Jboss JMX check """

    name = 'jboss'
    jmx_url = None

    OPTPARSE_MIN_NUMBER_OF_ARGS = 2
    OPTPARSE_MAX_NUMBER_OF_ARGS = 3

    def _myinit(self):
        """ init: override default url """
        self.jmx_url = self.config.get('jmx_url',
          'service:jmx:rmi://localhost/jndi/rmi://localhost:1090/jmxconnector')

    def _get(self, metric, *args, **kwargs):
        """ get metric - overrides _get from ZTCCheck """
        if metric == 'get_prop':
            # get jmx property
            return self.get_prop(*args)
        elif metric == 'ds':
            # get datasource info
            ds = args[0]
            metric = args[1]
            return self.get_ds_info(ds, metric)
        elif metric == 'heap':
            # get java heap memory info
            return self.get_heap(args[0])
        else:
            raise CheckFail('unsupported metric')

    def get_ds_info(self, ds, metric):
        """ Get jboss datasource info """
        mbean = 'jboss.jca:name=%s,service=ManagedConnectionPool' % ds
        return self.get_prop(mbean, metric)

    def get_heap(self, metric):
        """ get java heap memory metric: 'free', 'max', 'total' """
        metric = metric.capitalize() + 'Memory'
        return self.get_prop('jboss.system:type=ServerInfo', metric)
