'''
Created on Nov 10, 2014

@author: fechnert
'''

import copy
import re
import time
from models import ClientAction


class Feature(object):
    ''' Represents a abstract Feature '''

    def __init__(self, config, base_rules, queue, clients, channels):
        ''' Initialize the Object, set rules, apply rules '''
        self.config = config
        self.queue = queue
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
        ''' run the logic part on every matched client '''
        for clid, client in self.clients.items():
            try:
                client = self.filter(clid, client)
            except NotImplementedError:
                raise NotImplementedError
            if client:
                self.add_to_queue(client)

    def filter(self, clid, client):
        ''' Define the logic for a single client object.
            return client object to treat it
        '''
        raise NotImplementedError

    def add_to_queue(self, client_obj):
        ''' Add an action to the queue '''
        action = ClientAction(
            client_obj,
            self.__class__.__name__,
            self.config['execute']
        )
        if not str(action) in self.queue:
            self.queue.update({str(action): action})
        else:
            self.queue[str(action)].last_triggered = time.time()


class Test(Feature):
    ''' TESTCLASS: execute a configured action on all available clients '''
    def filter(self, clid, client):
        return client

class UsernameBlacklist(Feature):
    def filter(self, clid, client):
        for regex in self.config['name_blacklist']:
            if re.match(regex, client.client_nickname):
                return client

class OnAway(Feature):
    def filter(self, clid, client):
        if int(client.client_away) == 1:
            return client

class OnIdle(Feature):
    pass

class OnMute(Feature):
    def filter(self, clid, client):
        if int(client.client_input_muted) == 1:
            return client

class OnDeaf(Feature):
    pass
