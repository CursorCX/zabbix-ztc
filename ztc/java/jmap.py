#!/usr/bin/env python
#pylint: disable=W0232
'''
ZTC JMap class: runs jmap ... <pid>, caches results and parses output

Created on 17.12.2009

@author: vrusinov
'''

import os

from ztc.check import ZTCCheck
from ztc.store import ZTCStore


class Jmap(ZTCCheck):
    """
        Monitoring using jmap
    """
    pid = 0
    cache = 60  # how long store jmap cache
    jmap_path = '/usr/bin/jmap'

    def _get(self):
        raise NotImplementedError("Not implemented")

    def __myinit(self):
        #self.pid = int(pid)
        #self.config = ztc.commons.get_config('java')
        self.jmap_path = self.config.get('jmap_path', self.jmap_path)

    def _run_jmap_heap(self):
        cmd = "%s -heap %i" % (self.jmap_path, self.pid)
        f = os.popen(cmd)
        ret = ''
        l = f.read()
        while l:
            ret += l
            l = f.read()
        return ret

    def _load_jmap_heap(self):
        """
        Load jmap from cache or runs it
        """
        key = "jmap_heap_%i" % (self.pid,)
        c = ZTCStore(key, self.options, self.logger, ttl=60)
        jmap_heap = c.get()
        if jmap_heap:
            ret = jmap_heap.data
        else:
            # no data in cache
            jmap_heap_data = self._run_jmap_heap()
            if jmap_heap_data:
                c.set(jmap_heap_data)
                ret = jmap_heap
            else:
                ret = None
        return ret
