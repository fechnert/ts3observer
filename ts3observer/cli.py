'''
Created on Nov 9, 2014

@author: fechnert
'''

import sys
import time
import logging
from ts3observer.observer import Supervisor


class CommandLineInterface(object):
    ''' Represents the commandline '''

    def __init__(self):
        ''' Initialize the Config '''
        logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='[%(levelname)s] %(message)s')
        self.supervisor = Supervisor()

    def run(self):
        ''' Do some stuff '''
        while True:
            start = time.time()
            self.supervisor.execute()
            end = time.time()

            time_needed = end - start
            if time_needed >= self.supervisor.work_interval:
                logging.warn('More time needed than configured! ({} > {})'.format(time_needed, self.supervisor.work_interval))
            else:
                # logging.info('Sleeping {} seconds ...'.format(self.supervisor.work_interval - time_needed))
                time.sleep(self.supervisor.work_interval - time_needed)
