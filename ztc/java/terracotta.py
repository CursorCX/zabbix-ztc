#!/usr/bin/env python
"""
    Terracotta check class for ZTC. Licensed under the same terms as ZTC.

    Copyright (c) 2011 Wrike, Inc. [http://www.wrike.com]
    Copyright (c) 2011 Vladimir Rusinov <vladimir@greenmice.info>

Interesing Terracotta beans:

java.lang:name=Code Cache,type=MemoryPool:
  %8   - Type (java.lang.String, r)
    'NON_HEAP'
  %9   - Usage (javax.management.openmbean.CompositeData, r):
    Usage = {
      committed = 2359296;
      init = 2359296;
      max = 50331648;
      used = 628864;
    };
  %10  - UsageThreshold (long, rw)
  %11  - UsageThresholdCount (long, r)
  %12  - UsageThresholdExceeded (boolean, r)
  %13  - UsageThresholdSupported (boolean, r)
  %14  - Valid (boolean, r)
java.lang:name=CodeCacheManager,type=MemoryManager
java.lang:name=PS Eden Space,type=MemoryPool
java.lang:name=PS MarkSweep,type=GarbageCollector
java.lang:name=PS Old Gen,type=MemoryPool
java.lang:name=PS Perm Gen,type=MemoryPool
java.lang:name=PS Scavenge,type=GarbageCollector
java.lang:name=PS Survivor Space,type=MemoryPool
java.lang:type=ClassLoading
java.lang:type=Compilation
java.lang:type=Memory
java.lang:type=OperatingSystem
java.lang:type=Runtime
java.lang:type=Threading
#domain = java.util.logging:
java.util.logging:type=Logging
#domain = org.terracotta:
org.terracotta:name=DSO,type=Terracotta Server
org.terracotta:name=ObjectManagement,subsystem=Object Management,\
    type=Terracotta Server
org.terracotta:name=Terracotta Statistics Gatherer,subsystem=Statistics,\
    type=Terracotta Server
#domain = org.terracotta.internal:
org.terracotta.internal:name=Application Events,type=Terracotta Server
org.terracotta.internal:name=L2Dumper,type=Terracotta Server
org.terracotta.internal:name=Logger,type=Terracotta Server
org.terracotta.internal:name=Terracotta Lock Statistics,type=Terracotta Server
org.terracotta.internal:name=Terracotta Server,type=Terracotta Server
org.terracotta.internal:name=Terracotta Statistics Emitter,\
    subsystem=Statistics,type=Terracotta Agent
org.terracotta.internal:name=Terracotta Statistics Gateway,\
    subsystem=Statistics,type=Terracotta Server
org.terracotta.internal:name=Terracotta Statistics Manager,\
    subsystem=Statistics,type=Terracotta Agent
"""

from ztc.java.jmx import JMXCheck
from ztc.check import CheckFail
from ztc.store import ZTCStore


class JMXTerracotta(JMXCheck):
    """ Generic JMX check """

    name = 'terracotta'

    OPTPARSE_MIN_NUMBER_OF_ARGS = 2
    OPTPARSE_MAX_NUMBER_OF_ARGS = 3

    def myinit(self):
        # override default url
        self.jmx_url = self.config.get('jmx_url',
                                       'service:jmx:jmxmp://localhost:9520')

    def _get(self, metric, *args, **kwargs):
        if metric == 'get_prop':
            # get jmx property
            return self.get_prop(*args)
        elif metric == 'heap':
            # get java heap memory info
            # supported metric under heap: commited, init, max, used
            return self.get_heap(args[0])
        elif metric == 'codecache':
            # get java Code Cache memory info
            # supported sub-metrics: commited, max, init, used
            # candidate for moving to jmx class
            return self.get_codecache(args[0])
        else:
            raise CheckFail('unsupported metric')

    def extract_val_from_dict(self, data, metric):
        """ extract value from java dictionary-like sting, like following:
        {
            committed = 257294336;
            init = 268435456;
            max = 257294336;
            used = 59949552;
        }
        """
        for line in data.splitlines():
            line = line.strip()
            if line.startswith(metric):
                return int(line.split()[-1][:-1])
        return None

    def get_codecache(self, metric):
        """ get java codecache memory (non-heap) metrics """
        self.logger.debug('in get_codecache')
        st = ZTCStore('java.terracotta.codecache', self.options)
        st.ttl = 60
        data = st.get()
        if not data:
            # no cache, get from jmx
            data = self.get_prop('java.lang:name=Code Cache,type=MemoryPool',
                                 'Usage')
            st.set(data)
        rt = self.extract_val_from_dict(data, metric)
        if rt is None:
            raise CheckFail('no such memory mertic')
        else:
            return rt

    def get_heap(self, metric):
        """ get terracotta heap memory metrics """
        st = ZTCStore('java.terracotta.heap', self.options)
        st.ttl = 60
        data = st.get()
        if not data:
            # no cache, get from jmx
            data = self.get_prop('java.lang:type=Memory', 'HeapMemoryUsage')
            st.set(data)

        rt = self.extract_val_from_dict(data, metric)
        if rt is None:
            raise CheckFail('no such memory mertic')
        else:
            return rt
