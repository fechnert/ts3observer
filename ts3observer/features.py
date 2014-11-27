'''
Created on Nov 10, 2014

@author: fechnert
'''

import logging


class Feature(object):
    ''' Represents a abstract Feature '''

    def __init__(self, config, clients, channels):
        ''' Initialize the Object '''
        self.config = config
        self.clients = clients
        self.channels = channels

    def run(self):
        raise NotImplementedError


class UsernameBlacklist(Feature):
    pass

class OnAway(Feature):
    pass

class OnIdle(Feature):
    pass

class OnMute(Feature):
    pass

class OnDeaf(Feature):
    pass
