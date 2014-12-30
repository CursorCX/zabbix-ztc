#!/usr/bin/python
"""
This file is part of ZTC and distributed under the same license.
http://bitbucket.org/rvs/ztc/

Copyright (c) 2011 Wrike, Inc [http://www.wrike.com]
Copyright (c) 2011 Vladimir Rusinov <vladimir@team.wrike.com>
"""

from ztc.net.http import HTTP

h = HTTP()
h.get('ping', h.args[1])
