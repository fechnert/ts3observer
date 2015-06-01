''' This module contains all exceptions the ts3observer will use '''

import sys
import logging
import traceback


class Ts3observerBaseException(Exception):
    ''' The Base Exception of all evil.

        Uses unnamed arguments as objects for str.format().
            raise Ts3observerBaseException(some, variables)

        If you want to define own messaged for a Exception, simply give it the
        'msg' - named parameter:
            raise Ts3observerBaseException(msg='My own {} Message!'.format('Exception'))
    '''
    def __init__(self, *args, **kwargs):
        if 'msg' in kwargs.keys(): self.msg = kwargs['msg']
        super(Ts3observerBaseException, self).__init__(self.msg.format(*args))


class SkippableException(Ts3observerBaseException):
    ''' This kind of Exception will be raised at points where it is okay
        that there is a problem. Mostly at iterations over clients / channels.

        If this Exception is raised, the current iteration will ignore the
        exception-raising object and go on (like a 'continue' call in a loop).
    '''
    def execute(self):
        logging.warn('{}: {}'.format(self.__class__.__name__, self.msg))


class BreakingException(Ts3observerBaseException):
    ''' This Exceptions will be raised at points where it is not so okay
        That there is a problem. Mostly at iterations over clients / channels.

        If this Exception is raised, the current complete iteration will stop
        and the ts3observer goes to the next step in the code (like a 'break'
        call in a loop)
    '''
    def execute(self):
        logging.error('{}: {}'.format(self.__class__.__name__, self.msg))


class CriticalException(Ts3observerBaseException):
    ''' This Exception will be raised when shit is hitting the fan.
        If it's raised, the complete program will stop with nice traceback.
    '''
    pass


def _catch_exception(classname, function, *args, **kwargs):
    try:
        function(*args, **kwargs)
    except classname as e:
        e.execute()

def except_skippable(function, *args, **kwargs):
    _catch_exception(SkippableException, function, *args, **kwargs)

def except_breaking(function, *args, **kwargs):
    _catch_exception(BreakingException, function, *args, **kwargs)

def print_traceback():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb = traceback.format_exception(exc_type, exc_value, exc_traceback)
    for line in tb[:-1]:
        print line.rstrip('\r\n')

def print_buginfo():
    print 'You found a Bug? Report it! (https://github.com/HWDexperte/ts3observer/issues/new)'


#####
# Some global exceptions

class NoConfigFileException(CriticalException):
    msg = 'There is no \'/conf/ts3observer.conf\' file. Please copy the example and modify it!'

class ShutDownException(CriticalException):
    msg = 'Shutting down ...'

#####
# Telnet exceptions

class QueryFailedException(CriticalException):
    msg = 'The Query \'{}\' failed! {}'

#####
# Plugin Exceptions

class NewPluginDetected(CriticalException):
    msg = 'Stopping here to allow you to configure the created config files of new loaded Plugins!'

class NoMetaDataException(CriticalException):
    msg = 'The Plugin \'{}\' has no Meta class!'

class NoMetaAuthorNameException(CriticalException):
    msg = 'The Plugin \'{}\' has no author name in Meta class defined!'

class NoMetaAuthorEmailException(CriticalException):
    msg = 'The Plugin \'{}\' has no author email in Meta class defined!'

class NoMetaVersionException(CriticalException):
    msg = 'The Plugin \'{}\' has no version in Meta class defined!'

class NoDefaultConfigException(CriticalException):
    msg = 'The Plugin \'{}\' has no default config!'

class DefaultConfigisNotDictException(CriticalException):
    msg = 'The Plugin \'{}\'s default_config attr is not a dictionary!'
