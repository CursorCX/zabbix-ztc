#!/usr/bin/python
"""
nginx.* scripts item

This file is part of ZTC and distributed under GNU GPL v.3
Copyright (c) 2010-2011 Vladimir Rusinov <vladimir@greenmice.info>

Params:
    $1 - metric name. Supported:
        accepts - number of connection accepted by nginx (since server start)
        handled - number of connections handled by nginx (= accepts - rejected)
        requests - number of requests processed
        connections_active - current number of active connections
        connections_reading - current number of connections reading request
        connections_writing - current number of connections writing response
        connections_waiting - current number of connections on waiting state
"""

from ztc.nginx import NginxStatus

st = NginxStatus()
m = st.args[0]
st.get(m)
