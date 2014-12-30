#!/usr/bin/env python
# pylint: disable-msg=W0232
""" ZTC net.icmp package

Introduces ping check - can be used to do icmp ping
    from agents.

Limitations:
    * works only on *nix systems

Tested on:
    * GNU/Linux 2.6

This file is part of ZTC.
License: GPL v3
Copyright (c) 2011 Wrike, Inc. [http://www.wrike.com]
"""

from ztc.check import ZTCCheck
from ztc.myos import popen


class Ping(ZTCCheck):
    """ ztc ping check """
    name = "icmpping"

    OPTPARSE_MIN_NUMBER_OF_ARGS = 2
    OPTPARSE_MAX_NUMBER_OF_ARGS = 2

    def _get(self, metric, *args, **kwargs):
        """ metric is ignored for now """
        return self.icmpping(args[0])

    def icmpping(self, host):
        """Performs icmp ping using ping command

        Native python solution is possible, but would require it to run
        under root user. ping is suid on most systems, so no root required

        Args:
            host: string - hostname (or ip address)

        Returns:
            float - time to ping in seconds,
            int - 0 if failed"""
        cmd = "/bin/ping %s -c 1 -U -W 5" % host
        retcode, ret = popen(cmd, self.logger)
        if retcode == 0:
            # ping succeed
            ret = ret.strip().split("\n")[-1]  # pylint: disable-msg=E1103
            # ret is something like
            # rtt min/avg/max/mdev = 33.843/33.843/33.843/0.000 ms
            ret = ret.split('=')[1]
            ret = ret.strip()
            ret = float(ret.split('/')[0])
            return ret / 1000
        else:
            # ping unsuccessful
            return 0
