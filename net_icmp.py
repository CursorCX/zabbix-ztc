#!/usr/bin/python
"""
This file is part of ZTC and distributed under the same license.
http://bitbucket.org/rvs/ztc/

Copyright (c) 2011 Wrike, Inc [http://www.wrike.com]
"""

from ztc.net.icmp import Ping

p = Ping()
p.get('ping', p.args[1])
