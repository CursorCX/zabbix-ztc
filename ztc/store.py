#!/usr/bin/env python
# pylint: disable = R0201, W0702
""" ZTC Store class
Used for storing temporary values & cache

Copyright (c) 2010-2011 Vladimir Rusinov <vladimir@greenmice.info>
Copyright (c) 2011 Wrike, Inc. [http://www.wrike.com]
"""

import os
import time
import cPickle as pickle


class ZTCStore(object):
    """ class for storing data in key files """

    ## properties
    ttl = 7200  # default TTL for entry: 2 hours

    def __init__(self, name, options, ttl=7200, logger=None):
        """ Args:
        * name - name of store item
        * options = optparse options object. Needed for getting path of tmpdir
        """
        self.mydir = os.path.join(options.tmpdir, 'store')
        self.myfile = os.path.join(self.mydir, name)
        if not os.path.isdir(self.mydir):
            os.makedirs(self.mydir)
        self.ttl = ttl
        self.logger = logger

    def _mktmpdir(self, path):
        """ check & make tmp dir """
        if not os.path.isdir(path):
            os.makedirs(path)

    def get(self):
        """ retirn stored object """
        ret = None
        if os.path.isfile(self.myfile):
            if time.time() - os.stat(self.myfile).st_mtime > self.ttl:
                # do not store for more then ttl seconds
                self.clear()
            else:
                f = open(self.myfile, 'r')
                ret = pickle.load(f)
                f.close()
        return ret

    def set(self, val):
        """ set value """
        try:
            f = open(self.myfile, 'w')
            pickle.dump(val, f)
            f.close()
        except:
            # set should never fail
            if self.logger:
                self.logger.exception("set failed")

    def clear(self):
        """ clean up """
        os.unlink(self.myfile)
