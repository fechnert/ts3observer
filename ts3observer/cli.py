''' The cli module that will interact with your bash. '''

import sys
import logging

from ts3observer.observer import Supervisor
from ts3observer.utils import path, get_and_set_global_config, get_loglevel


class CommandLineInterface(object):
    ''' The cli will interact with your bash '''

    def __init__(self):
        self._set_logging_config()
        get_and_set_global_config()

    def _set_logging_config(self):
        ''' Set the basic logging config '''
        logging.basicConfig(
            stream=sys.stdout,
            level=get_loglevel(),
            format='[%(asctime)s][%(levelname)8s] %(message)s',
            datefmt='%d.%m.%Y - %H:%M:%S'
        )

    def run(self):
        ''' Run the ts3observer bot '''
        supervisor = Supervisor()

        supervisor.run()

    def version(self):
        f = open(path('/.version'), 'r')
        print(f.read().rstrip('\r\n'))
        f.close()
