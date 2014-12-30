#!/usr/bin/python
"""
PHP FPM check script

This file is part of ZTC and distributed under the same license.
http://bitbucket.org/rvs/ztc/

Copyright (c) 2011 Vladimir Rusinov <vladimir@greenmice.info>
"""

from ztc.php.fpm import PHPFPMCheck

p = PHPFPMCheck()
m = p.args[0]
p.get(m, *p.args[1:])
