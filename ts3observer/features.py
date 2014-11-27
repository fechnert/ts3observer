'''
Created on Nov 10, 2014

@author: fechnert
'''

import logging


class Feature(object):
    ''' Represents a abstract Feature '''

    def __init__(self, config, base_rules, clients, channels):
        ''' Initialize the Object '''
        self.config = config
        self.clients = clients
        self.channels = channels
        self._set_rules(base_rules)
        self._overwrite_rules(config)

    def _set_rules(self, base_rules):
        ''' Set the rules '''
        for rulename, rulelist in base_rules.items():
            setattr(self, rulename, rulelist)

    def _overwrite_rules(self, config):
        ''' Overwrite the base rules with specific '''
        if 'rules' in config:
            self._set_rules(config['rules'])

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
