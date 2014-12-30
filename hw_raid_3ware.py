#!/usr/bin/python
"""
3ware raid monitoring item script

Copyright (c) 2010-2011 Vladimir Rusinov <vladimir@greenmice.info>
Copyright (c) 2010 Murano Software [http://muranosoft.com]
"""

import ztc.hw

tw = ztc.hw.RAID_3Ware()
tw.get('status')
