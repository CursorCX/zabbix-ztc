#!/usr/bin/env python
#pylint: disable=W0232
"""
    ZTC Hardware monitoring package

    Copyright (c) 2010-2011 Vladimir Rusinov <vladimir@greenmice.info>
    Copyright (c) 2010 Murano Software [http://muranosoft.com]
    Copyright (c) 2011 Parchment Inc. [http://www.parchment.com]
"""

from ztc.check import ZTCCheck, CheckFail
from ztc.myos import popen


class RAID_3Ware(ZTCCheck):
    """
        Class for monitoring 3ware raid.
        Requirements:
            * tw_cli tool installed
            * run as root, or have permissions to run tw_cli
    """

    name = 'hw_raid_3ware'

    _tw_out = {}

    # pylint: disable=W0613
    def _get(self, metric, *arg, **kwarg):
        if metric == 'status':
            return self.get_status()
        else:
            raise CheckFail('uncknown metric')

    def _read_tw_status(self, c=0, u=0, cmd='status'):
        key = (c, u, cmd)
        if key in self._tw_out:
            # already executed
            return self._tw_out[key]
        else:
            command = "%s info c%i u%i %s" \
                % (self.config.get('tw_cli_path', '/opt/3ware/tw_cli'),
                    c,
                    u,
                    cmd)
            # pylint: disable=W0612
            retcode, ret = popen(command, self.logger)  # @UnusedVariable
            self._tw_out[key] = ret
            return ret

    def get_status(self, c=0, u=0):
        """ get status of raid

        Args:
            c: controller numbe
            u: unit (array) number

        Returns:
            'OK' if status is in optimal config
            != 'OK' if it isn't
        """
        ret = "ZTC_FAIL"
        try:
            # pylint: disable=E1103
            st = self._read_tw_status(c, u, 'status')
            ret = st.splitlines()[0].split()[3]
        except IndexError:
            self.logger.exception(
                "problem with tw_cli output. "
                "Make sure it's installed correctly")
            ret = "ZTC_FAIL: TW_CLI"
        except AttributeError:
            self.logger.exception("popen returned incorrect type. Please, "
                                  "report a bug")
            ret = "ZTC_FAIL: popen"
        except:
            self.logger.exception("uncknown exception")
            ret = "ZTC_FAIL"
        return ret

if __name__ == '__main__':
    # test
    tw = RAID_3Ware()
    print tw.get_status()
