'''
Created on Nov 9, 2014

@author: fechnert
'''

import sys
import logging
from ts3observer.observer import Supervisor


class CommandLineInterface(object):
    ''' Represents the commandline '''

    def __init__(self):
        ''' Initialize the Config '''
        logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='[%(levelname)5s] %(message)s')
        self.supervisor = Supervisor()

    def run(self):
        ''' Do some stuff '''
        self.supervisor.execute()
