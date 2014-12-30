#!/usr/bin/env python
# pylint: disable=W0221,W0702,W0201
"""
ZTCCheck class - wrapper for ztc checks
provides logging, output formatting and error handling abilities

This file is part of ZTC

Copyright (c) 2011 Denis Seleznyov [https://bitbucket.org/xy2/]
Copyright (c) 2011-2012 Vladimir Rusinov <vladimir@greenmice.info>
Copyright (c) 2011-2012 Murano Software [http://muranosoft.com]

License: GNU GPL3
"""

import os
import sys
import traceback
import optparse
import ConfigParser
import logging  # @UnusedImport
import logging.handlers  # @UnusedImport

import unittest

from ztc.myrotatingfilehandler import MyRotatingFileHandler


class CheckFail(Exception):
    """Exception that should be raised to notify zabbix about failed check."""
    pass


class CheckTimeout(Exception):
    """Exception that should be raised to notify zabbix that check timeouted"""
    pass


class MyConfigParser(ConfigParser.ConfigParser):
    """ Wrapper around ConfigParser to provide nicer API for ztc """

    def __init__(self, section='main'):
        self.sectname = section
        ConfigParser.ConfigParser.__init__(self)

    def get(self, option, default):
        try:
            return ConfigParser.ConfigParser.get(self, self.sectname, option)
        except:
            return default


class ZTCCheck(object):
    """Base class for ztc checks"""

    # shortened name of the class
    # being used for getting config
    name = 'ztccheck'
    ver = "11.07"
    args = []  # parsed command-line args

    # minimum & maximum number of command-line arguments
    OPTPARSE_MIN_NUMBER_OF_ARGS = 0
    OPTPARSE_MAX_NUMBER_OF_ARGS = 0

    debug = False
    test = False
    logger = None

    def __init__(self, name=None):
        if name:
            self.name = name
        if self.name == 'ztccheck':
            raise NotImplementedError("Class %s must redefine its name"
                                            % (self.__class__.__name__,))
        self._parse_argv()
        self.config = self._get_config()
        # checking if we are running in debug mode
        if self.config.get('debug', False):
            self.debug = True

        self._setup_logging()
        self._myinit()

    def _setup_logging(self):
        """Setup logging - self.logger"""
        # setup logger
        self.logger = logging.getLogger(self.__class__.__name__)
        formatter = logging.Formatter(
            "[%(name)s] %(asctime)s - %(levelname)s: %(message)s")
        # setting file handler
        h = MyRotatingFileHandler(
                                  self.options.logfile,
                                  "a",
                                  1 * 1024 * 1024,  # max 1 M
                                  10)  # max 10 files
        if self.debug:
            # setting stream handler
            sh = logging.StreamHandler()
            sh.setLevel(logging.DEBUG)
            self.logger.setLevel(logging.DEBUG)
            sh.setFormatter(formatter)
            h.setLevel(logging.DEBUG)
            self.logger.addHandler(sh)
        else:
            self.logger.setLevel(logging.WARN)
            h.setLevel(logging.WARN)
        h.setFormatter(formatter)
        self.logger.addHandler(h)
        self.logger.debug("created")
        self.logger.debug("config file: %s" % \
                          os.path.join(self.options.confdir,
                          self.name + ".conf"))

    def _myinit(self):
        """ To be overriden by subclasses, executes just after __init__ -
        in order to avoid messing with parent's __init__ in subclasses """
        pass

    def _parse_argv(self):
        """ Parse command-line arguments """
        parser = optparse.OptionParser()
        parser.add_option("-v", "--version",
                  action="store_true", dest="version", default=False,
                  help="show version and exit")
        parser.add_option("-d", "--debug",
                  action="store_true", dest="debug", default=False,
                  help="enable debug")
        parser.add_option("-t", "--tmpdir",
                  action="store", type="str", dest="tmpdir",
                  default="/tmp/ztc/", help="Temp direcroty path")
        parser.add_option("-l", "--logfile",
                  action="store", type="str", dest="logfile",
                  default="/var/log/zabbix/ztc.log")
        parser.add_option("-c", "--confdir",
                  action="store", type="str", dest="confdir",
                  default="/usr/local/shell/zabbix/ztc/conf/", help="ZTC Config dir")
        parser.add_option("-i", "--instance", dest="instname", default="main",
                          action="store", type="str")
        (options, args) = parser.parse_args()

        if options.version:
            self.version()
            sys.exit(0)

        if options.debug:
            self.debug = True

        self.options = options
        self.args = args
        if self.OPTPARSE_MIN_NUMBER_OF_ARGS > self.OPTPARSE_MAX_NUMBER_OF_ARGS:
            self.OPTPARSE_MAX_NUMBER_OF_ARGS = self.OPTPARSE_MIN_NUMBER_OF_ARGS
        #number_of_args = len(self.args)
        #if number_of_args < self.OPTPARSE_MIN_NUMBER_OF_ARGS:
        #    raise CheckFail("Not enough arguments")
        #if number_of_args > self.OPTPARSE_MAX_NUMBER_OF_ARGS:
        #    raise CheckFail("Not enough arguments")

    def version(self):
        """ print version information """
        print "ZTC version %s" % self.ver
        print "http://trac.greenmice.info/ztc/"

    def _get_config(self):
        """ return config object
        WARN: no logger object available here
        """
        config = MyConfigParser(self.options.instname)
        config.read(os.path.join(self.options.confdir, self.name + ".conf"))
        return config

    def _get(self, metric, *args, **kwargs):  # pylint: disable-msg=W0613
        """This method MUST return exactly one string or integer or raise
        one of CheckFail or CheckTimeout exceptions. Multiple return values
        are not supported by zabbix yet. Default behavour is to return
        attribute name. Should be overriden if more params needed"""
        return self.__getattribute__(metric)

    def get_val(self, metric=None, *args, **kwargs):
        """ wrapper above _get to ensure every returned value is in
        correct format """
        # TODO: run _get in another thread, terminate it when it's running
        # for too long.
        # This is required for zabbix agent not to hang
        ret = self._get(metric, *args, **kwargs)
        if type(ret) == float:
            # prevent from printing in exp form
            ret = ("%.6f" % ret).rstrip('0').rstrip('.')
        return ret

    def get(self, metric=None, *args, **kwargs):
        """Perform a check and return data immediately with exit code
        expected by zabbix. Caller script will be not continued after this
        method call, so SomeFancyCheck.get(arg1, arg2, ...) line should
        be last in userparameter script. Exit codes are defined in enum
        ZBX_SYSINFO_RET (include/sysinfo.h)"""
        self.logger.debug("executed get metric '%s', args '%s', kwargs '%s'" %
                   (str(metric), str(args), str(kwargs)))
        try:
            ret = self.get_val(metric, *args, **kwargs)
            print(ret)
        except CheckFail, e:
            self.logger.exception('Check fail, getting %s' % (metric,))
            if self.debug:
                traceback.print_stack()
            for arg in e.args:
                print(arg)
            sys.exit(1)
        except CheckTimeout, e:
            self.logger.exception('Check timeout, getting %s' % (metric,))
            if self.debug:
                traceback.print_stack()
            for arg in e.args:
                print(arg)
            sys.exit(2)
        except Exception, e:
            # totally unexpected fail: dump all data we know
            self.logger.exception('Check unexpected error, getting %s' % \
                                  (metric,))
            sys.exit(1)
        #sys.exit(0)

if __name__ == '__main__':
    unittest.main()
