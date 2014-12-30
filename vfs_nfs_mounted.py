#!/usr/bin/python
"""
NFS template items script

Copyright (c) 2011 Vladimir Rusinov <vladimir@greenmice.info>
Copyright (c) 2011 Wrike, Inc. [http://www.wrike.com]
Copyright (c) 2011 Murano Software [http://muranosoft.com]


This file is part of ZTC and distributed under GNU GPL v.3
Copyright (c) 2010 Vladimir Rusinov <vladimir@greenmice.info>
"""

from ztc.system.vfs.nfs import NFSMounted

ch = NFSMounted()
ch.get('mounted')
