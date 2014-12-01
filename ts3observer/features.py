'''
Created on Nov 10, 2014

@author: fechnert
'''

import logging
import copy


class Feature(object):
    ''' Represents a abstract Feature '''

    def __init__(self, config, base_rules, clients, channels):
        ''' Initialize the Object, set rules, apply rules '''
        self.config = config
        self.clients = copy.copy(clients)
        self.channels = channels
        self._set_rules(base_rules)
        self._overwrite_rules(config)
        self._apply_rules()

    def _set_rules(self, base_rules):
        ''' Set the rules '''
        for rulename, rulelist in base_rules.items():
            setattr(self, rulename, rulelist)

    def _overwrite_rules(self, config):
        ''' Overwrite the base rules with specific '''
        if 'rules' in config:
            self._set_rules(config['rules'])

    def _apply_rules(self):
        ''' Apply white- and blacklist rules to feature '''
        for clid, client in self.clients.items():
            self.__apply_client_rules(clid, client)
            self.__apply_group_rules(clid, client)
            self.__apply_channel_rules(clid, client)

    def __apply_client_rules(self, clid, client):
        if self.client_whitelist:
            if not client.client_unique_identifier + '=' in self.client_whitelist:
                self.clients.pop(clid, None)
        if self.client_blacklist:
            if client.client_unique_identifier + '=' in self.client_blacklist:
                self.clients.pop(clid, None)

    def __apply_group_rules(self, clid, client):
        if self.group_whitelist:
            if not client.client_servergroups in self.group_whitelist:
                self.clients.pop(clid, None)
        if self.group_blacklist:
            if client.client_servergroups in self.group_blacklist:
                self.client.pop(clid, None)

    def __apply_channel_rules(self, clid, client):
        if self.channel_whitelist:
            if not client.cid in self.channel_whitelist:
                self.clients.pop(clid, None)
        if self.channel_blacklist:
            if client.cid in self.channel_blacklist:
                self.clients.pop(clid, None)

    def run(self):
        raise NotImplementedError

    def treat_client(self, client_obj):
        ''' execute configured action to client '''
        getattr(client_obj, self.config['execute']['action'])(
            self.__class__.__name__, **self.config['execute']
        )


class Test(Feature):
    ''' TESTCLASS: execute a configured action on all available clients '''
    def run(self):
        for clid, client in self.clients.items():
            self.treat_client(client)

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
