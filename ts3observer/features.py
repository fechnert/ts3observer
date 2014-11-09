'''
Created on Nov 10, 2014

@author: fechnert
'''

import logging


class Feature(object):
    ''' Represents a abstract Feature '''

    def __init__(self, config):
        ''' Initialize the Config '''
        self.config = config

    def run(self):
        raise NotImplementedError


class UsernameBlacklist(Feature):
    pass


class AutoMove(Feature):
    pass


class MusicbotDetect(Feature):
    pass
