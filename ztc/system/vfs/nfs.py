#!/usr/bin/env python
'''
NFS Mounted check class for ZTC

Copyright (c) 2011 Wrike, Inc. [http://www.wrike.com/]
'''

from ztc.check import ZTCCheck, CheckFail

from ztc.system.vfs import MountStatus


class NFSMounted(ZTCCheck):
    name = 'nfs'

    def _get(self, metric=None, *args, **kwargs):
        if metric == 'mounted':
            return self.get_mounted()
        else:
            CheckFail("Uncknown metric: %s" % metric)

    def get_mounted(self):
        mount_point = self.config.get('mountpoint', '/mnt/nfs')

        ms = MountStatus(mount_point)
        return int(ms.checkmount('nfs'))
