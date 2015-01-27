'''
Created on Dec 1, 2014

@author: fechnert
'''

import logging
import time
from utils import Escaper


class ClientAction(object):
    ''' Represents a action for clients to treat them '''

    def __init__(self, client_obj, featurename, additional_params):
        self.client_obj = client_obj
        self.featurename = featurename
        self.additional_params = additional_params
        self._set_trigger_time()
        self._set_last_triggered()

    def _set_trigger_time(self):
        ''' Get the delay of a action and add it to current time as trigger time '''
        try: s_delay = self.additional_params['s_delay']
        except KeyError: s_delay = 0
        try: m_delay = self.additional_params['m_delay']
        except KeyError: m_delay = 0

        if s_delay and m_delay:
            logging.warn('{}: s_delay and m_delay set ... ignoring both!'.format(self.featurename))
            delay = 0
        elif m_delay:
            delay = m_delay * 60
        else:
            delay = s_delay
        self.trigger_time = time.time() + delay

    def _set_last_triggered(self):
        ''' Sets the current time as last triggered '''
        self.last_triggered = time.time()

    def __repr__(self):
        return '<{featurename}_{actionname}_clid={clid}>'.format(
            featurename=self.featurename,
            actionname=self.additional_params['action'].capitalize(),
            clid=self.client_obj.clid
        )


class Client(object):
    ''' Represents the client '''

    def __init__(self, clid, **kwargs):
        ''' Fill the object dynamically with client attributes got from telnet '''
        self.clid = clid
        self.__set_variables(kwargs.items())
        self.__alter_values()
        self.__split_servergroups()

    def __set_variables(self, variables):
        ''' Set the additional variables '''
        for key, value in variables:
            setattr(self, key, value)

    def __alter_values(self):
        ''' Alternate some values '''
        self.cid = int(self.cid)
        self.decoded_nickname = Escaper.decode(self.client_nickname)

    def __split_servergroups(self):
        ''' Split the servergroups '''
        if self.client_servergroups:
            self.client_servergroups = map(lambda g: int(g), self.client_servergroups.split(','))

    def __repr__(self):
        return '{}'.format(Escaper.decode(self.client_nickname))


class Channel(object):
    ''' Represents the Channel '''

    def __init__(self, socket, **kwargs):
        ''' Fill the object dynamically with channel attributes got from telnet '''
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return '<Channel object ({})>'.format(self.channel_name)

    def delete(self):
        ''' Delete a channel '''
        raise NotImplementedError
