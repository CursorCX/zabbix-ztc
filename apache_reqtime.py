#!/usr/bin/python
'''
Gets average apache request time

Copyright (c) 2010-2011 Vladimir Rusinov <vladimir@greenmice.info>

Params:
    $1 - metric name. Supported: avg, min, max. Defaults to avg

Usage:

1. Configure apache:
   `LogFormat "%D <whatever>" timelog` in modules.d/00_mod_log_config.conf (or
        elsewhere, this is distro-specific)
   `CustomLog /var/log/apache2/time.log timelog` there and in every vhost
2. Configure sudo to allow run /opt/ztc/ping/apache_reqtime.py <arg>
'''

from ztc.apache import ApacheTimeLog

tl = ApacheTimeLog()
if len(tl.args) == 0:
    m = 'avg'
else:
    m = tl.args[0]
tl.get(m)
