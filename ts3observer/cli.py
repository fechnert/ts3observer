'''
Created on Nov 9, 2014

@author: fechnert
'''

import sys
import time
import logging
import argparse
from ts3observer.observer import Supervisor


class CommandLineInterface(object):
    ''' Represents the commandline '''

    def __init__(self):
        ''' Initialize the Config '''
        self._parse_arguments()
        logging.basicConfig(stream=sys.stdout, level=self._get_loglevel(), format='[%(levelname)s] %(message)s')
        self.supervisor = Supervisor()

    def _parse_arguments(self):
        ''' Parse runtime arguments '''
        parser = argparse.ArgumentParser()
        parser.add_argument('-v', '--verbose', action='store_true', help='Increase verbosity for debugging purpose')
        self.args = parser.parse_args()

    def _get_loglevel(self):
        ''' Get the loglevel out of the runtime arguments '''
        if self.args.verbose:
            return logging.DEBUG
        else:
            return logging.INFO

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
