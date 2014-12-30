#!/usr/bin/python
"""
apache.* scripts item

This file is part of ZTC and distributed under GNU GPL v.3
Copyright (c) 2010-2011 Vladimir Rusinov
Copyright (c) 2010 Murano Software [http://muranosoft.com/]

Params:
    $1 - metric name. Supported:
        ping - ping to apache (time of test page load)
        accesses - number of accesses since server start
        traffic - number of bytes sent since server start
        workers_busy - current number of busy workers
        workers_closingconn - current number of workers closing connection
        workers_dns - current number of workers doing dns query
        workers_finishing - current number of workers finishing
        workers_idle - current number of idle workers
        workers_idlecleanup - current number of idle workers in cleanup state
        workers_keepalive - current number of workers in keepalive state
        workers_logging - current number of workers in logging state
        workers_openslot - current number of open slots for workers
        workers_reading - current number of workers in reading state
        workers_starting - current number of workers starting
        workers_waitingconn - current number of workers ready to accept
                              connection
        workers_writing - current number of workers writing response
Returns:
    for ping: float (seconds)
    for others: int (bytes or number of)
"""

from ztc.apache import ApacheStatus

st = ApacheStatus()
m = st.args[0]
st.get(m)
