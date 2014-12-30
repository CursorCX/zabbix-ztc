#!/usr/bin/env python
"""ZTC-wide test customs functions and mocks"""

import os
import logging


def setup_no_logging(self):
    """Mock for ZTCCheck._setup_logging function"""
    # setup logger
    self.logger = logging.getLogger(self.__class__.__name__)
    formatter = logging.Formatter(
        "[%(name)s] %(asctime)s - %(levelname)s: %(message)s")

    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    self.logger.setLevel(logging.DEBUG)
    sh.setFormatter(formatter)
    self.logger.addHandler(sh)
    self.logger.debug("created")
    self.logger.debug("config file: %s" % \
                      os.path.join(self.options.confdir,
                      self.name + ".conf"))
