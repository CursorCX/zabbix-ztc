#!/usr/bin/python
"""
vfs_dev_* scripts item


This file is part of ZTC and distributed under GNU GPL v.3
Copyright (c) 2010 Murano Software [http://muranosoft.com/]

Params:
    $1 - metric name. Supported:
        major: major number
        minor: minor mumber
        devname: device name
        reads: reads completed succesfully
        reads_merged: reads merged
        sectors_read: sectors read
        time_read: time spent reading (ms)
        writes: writes completed
        writes_merged: writes merged
        sectors_written: sectors written
        time_write: time spent writing (ms)
        cur_ios: I/Os currently in progress
        time_io: time spent doing I/Os (ms)
        time_io_weidged: weighted time spent doing I/Os (ms)

        health - smart disk health
    $2 - device name, e.g. 'sda'
"""

from ztc.system.vfs import DiskStatus


d = DiskStatus()
m = d.args[0]
d.get(m, *d.args[1:])
