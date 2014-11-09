'''
Created on Nov 9, 2014

@author: fechnert
'''

from ts3observer.observer import Configuration


class CommandLineInterface(object):
    ''' Represents the commandline '''

    def __init__(self):
        ''' Do some stuff '''
        self.config = Configuration('config.yml')

    def run(self):
        ''' Do some stuff '''
        print self.config