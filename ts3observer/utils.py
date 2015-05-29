''' Define some utils for all needs '''

import logging
from ts3observer import Configuration
from ts3observer.exc import NoConfigFileException


def path(string):
    ''' Return a relative path to any file in this project, given by string '''
    return '{}{}'.format(ts3o.base_path, string)

def get_and_set_global_config():
    ''' Get the global configuration and store it in the ts3o object.
        Do not call before a logging config is set because of the beauty.
    '''
    try:
        ts3o.config = Configuration(path('/conf/ts3observer.yml'))
    except IOError:
        raise NoConfigFileException()

def get_loglevel():
    if ts3o.args.verbose:
        return logging.DEBUG
    if ts3o.args.quiet:
        return logging.CRITICAL
    return logging.INFO
