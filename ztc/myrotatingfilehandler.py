#!/usr/bin/env
"""
MyRotatingFileHandler - python logger file handler with file rotation and
ability to set owner/permissons on created file

Copyright (c) 2009 Cory Engebretson,
    http://stackoverflow.com/users/3406/cory-engebretson
    http://stackoverflow.com/questions/1407474/
"""

from logging import handlers

import os
import stat

import pwd


class MyRotatingFileHandler(handlers.RotatingFileHandler):
    """ RotatingFileHandler with setting custom owner and permissions """

    def _open(self):
        st = handlers.RotatingFileHandler._open(self)
        self.chuid()
        return st

    #def doRollover(self):
    #    """
    #    Override base class method to make the new log file group writable.
    #    """
    #    # Rotate the file first.
    #    handlers.RotatingFileHandler.doRollover(self)
    #    self.chuid()

    def chuid(self):
        # Add group write to the current permissions.
        try:
            currMode = os.stat(self.baseFilename).st_mode
            os.chmod(self.baseFilename, currMode | stat.S_IWGRP)
        except OSError:
            pass
        try:
            if os.getuid() == 0:
                uid = pwd.getpwnam('zabbix').pw_uid
                gid = pwd.getpwnam('zabbix').pw_gid
                os.chown(self.baseFilename, uid, gid)
        except KeyError:
            pass
