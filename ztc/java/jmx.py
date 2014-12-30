#!/usr/bin/env python
"""
JMX Check class for ZTC. Licensed under the same terms as ZTC.

Copyright (c) 2011 Wrike, Inc. [http://www.wrike.com]
Copyright (c) 2011-2012 Vladimir Rusinov <vladimir@greenmice.info>

Usage example to jmxterm-*.jar:

java -Djava.endorsed.dirs=/opt/ztc/lib/ -jar \
    /opt/ztc/lib/jmxterm-1.0-alpha-4-uber.jar -l \
    service:jmx:jmxmp://localhost:9520
get -b java.lang:type=ClassLoading LoadedClassCount -s

automated version:

echo "get -b java.lang:type=ClassLoading LoadedClassCount -s" | java \
    -Djava.endorsed.dirs=/opt/ztc/lib/ -jar \
    /opt/ztc/lib/jmxterm-1.0-alpha-4-uber.jar -l \
    service:jmx:jmxmp://localhost:9520 -e -n -v silent

"""

from ztc.check import ZTCCheck, CheckFail
from ztc.myos import popen


class JMXCheck(ZTCCheck):
    """ Generic JMX check """

    name = 'java'

    OPTPARSE_MIN_NUMBER_OF_ARGS = 3

    def _myinit(self):
        """ constructor override """
        self.jmx_url = self.config.get('jmx_url',
                                       'service:jmx:rmi://localhost:123')

    def _get(self, metric, *args, **kwargs):
        if metric == 'get_prop':
            # get jmx property
            return self.get_prop(*args)
        else:
            raise CheckFail('unsupported metric')

    def get_prop(self, mbean_name, attribute_name):
        """ get custom JMX bean property """

        # escape spaces in mbean_name
        mbean_name = mbean_name.replace(' ', '\ ')

        popen_cmd = "java -Djava.endorsed.dirs=/opt/ztc/lib/ -jar " + \
            "/opt/ztc/lib/jmxterm-1.0-alpha-4-uber.jar -l %s -e -n " + \
            "-v silent" % (self.jmx_url,)
        jmxterm_cmd = "get -b %s %s -s" % (mbean_name, attribute_name)
        self.logger.debug("Executing jmxterm command %s" % jmxterm_cmd)
        self.logger.debug("Jmxterm executable: %s" % popen_cmd)
        try:
            code, ret = popen(popen_cmd, self.logger, jmxterm_cmd)
        except IOError:
            self.logger.exception("Failed to run popen")
            raise CheckFail("jmxterm call failed")
        if code != 0:
            self.logger.error('jmxterm returned non-zero status')
            raise CheckFail('unable to get jmx propery %s %s' %
                            (mbean_name, attribute_name))
        return ret.strip()
