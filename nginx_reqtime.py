#!/usr/bin/python
"""
Nginx TimeLog check script: calculates min/avg/max upstream response times.

Usage:
1. configure time_log log format in nginx config (http section):
log_format time_log '$upstream_response_time $request <anything you want>';

2. Add timelog log to all servers/locations you need to monitor:
access_log /var/log/nginx/time.log time_log;

3. Check log path on config file /etc/ztc/nginx.conf

4. Make sure zabbix can execute nginx_reqtime.py script under root (to allow
cleaning of the log)

5. It might be good idea to place this log to tmpfs.

This file is part of ZTC and distributed under the same license.
http://bitbucket.org/rvs/ztc/

Copyright (c) 2011 Vladimir Rusinov <vladimir@greenmice.info>
"""

from ztc.nginx.timelog import NginxTimeLog

st = NginxTimeLog()
m = st.args[0]
st.get(m)
