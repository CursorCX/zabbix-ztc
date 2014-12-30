#!/usr/bin/python
"""
vfs.mdstat.failed_devs scripts item


This file is part of ZTC and distributed under GNU GPL v.3
Copyright (c) 2010 Vladimir Rusinov <vladimir@greenmice.info>
"""

from ztc.system.vfs import  MDStatus

md = MDStatus()
md.get('failed_devs')
