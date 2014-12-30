#!/usr/bin/python
"""
net.conn item sctipt

This file is part of ZTC and distributed under GNU GPL v.3
Copyright (c) 2010 Vladimir Rusinov <vladimir@greenmice.info>
Copyright (c) 2010 Murano Software [http://muranosoft.com]
Copyright (c) 2010 Wrike, Inc. [http://wrike.com]

Params:
    $1 - metric name. Supported:
        'ALL'
        'ESTABLISHED'
        'SYN_SENT'
        'SYN_RECV'
        'FIN_WAIT1'
        'FIN_WAIT2'
        'TIME_WAIT'
        'CLOSE'
        'CLOSE_WAIT'
        'LAST_ACK'
        'LISTEN'
        'CLOSING'
    Returns:
        stdout: int, number of items in specified state
"""

from ztc.net import Conn

c = Conn()
if len(c.args) == 0:
    m = 'ALL'
else:
    m = c.args[0]
c.get(m)
