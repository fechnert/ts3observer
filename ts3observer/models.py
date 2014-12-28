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

    def execute(self):
        ''' Execute this action on the client '''
        return getattr(self.client_obj, self.additional_params['action'])(
            self.featurename,
            **self.additional_params
        )

    def __repr__(self):
        return '<{featurename}_{actionname}_clid={clid}>'.format(
            featurename=self.featurename,
            actionname=self.additional_params['action'].capitalize(),
            clid=self.client_obj.clid
        )

class MoveBackAction(object):
    ''' This is a helper class to move back clients which have been moved '''

    def __init__(self, clid, to, feature_name, trigger_time):
        ''' initialize the object '''
        self.clid = clid
        self.to = to
        self.feature_name = feature_name
        self.trigger_time = trigger_time

    def __repr__(self):
        return '<{featurename}_moveback_{clid}>'.format(
            featurename=self.feature_name,
            clid=self.clid
        )


class Client(object):
    ''' Represents the client '''

    def __init__(self, clid, socket, **kwargs):
        ''' Fill the object dynamically with client attributes got from telnet '''
        self.clid = clid
        self.socket = socket
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.__alter_values()
        self.__split_servergroups()

    def __alter_values(self):
        ''' Alternate some values '''
        self.cid = int(self.cid)

    def __split_servergroups(self):
        ''' Split the servergroups '''
        if self.client_servergroups:
            self.client_servergroups = map(lambda g: int(g), self.client_servergroups.split(','))

    def __repr__(self):
        return '<{}>'.format(Escaper.decode(self.client_nickname))

    @Escaper.encode_attr('reason')
    def kick(self, featurename, reasonid, reason='ByeBye', **kwargs):
        ''' Kick a client '''
        self.socket.write('clientkick reasonid={} reasonmsg={} clid={}\n'.format(reasonid, reason, self.clid))
        self.socket.read_until('msg=ok', 2)
        logging.info('Feature \'{}\' kicked {}'.format(featurename, Escaper.decode(self.client_nickname)))

    def move(self, featurename, to, **kwargs):
        ''' Move a client :to: a channel '''
        if int(self.cid) != to:
            self.ocid = self.cid
            self.cid = to
            self.socket.write('clientmove cid={} clid={}\n'.format(to, self.clid))
            self.socket.read_until('msg=ok', 2)
            logging.info('Feature \'{}\' moved {} (from cid {} to {})'.format(featurename, Escaper.decode(self.client_nickname), self.ocid, to))
            return True
        else:
            self.ocid = to
            return False

    @Escaper.encode_attr('reason')
    def ban(self, featurename, time=0, reason='Kicked', **kwargs):
        ''' Ban a client for :sfor: seconds '''
        if time:
            self.socket.write('banclient clid={} banreason={} time={}\n'.format(self.clid, reason, time))
        else:
            self.socket.write('banclient clid={} banreason={}\n'.format(self.clid, reason))
        self.socket.read_until('msg=ok', 2)
        logging.info('Feature \'{}\' banned {} for {} seconds (0 = infinite)'.format(featurename, Escaper.decode(self.client_nickname), time))

    def show(self, featurename, **kwargs):
        ''' Only shows the clientname (for debugging purpose) '''
        logging.info('{}: {}'.format(featurename, Escaper.decode(self.client_nickname)))

    @Escaper.encode_attr('message')
    def poke(self, featurename, message, **kwargs):
        ''' Poke a client with given message '''
        self.socket.write('clientpoke clid={} msg={}\n'.format(self.clid, message))
        self.socket.read_until('msg=ok', 2)

    @Escaper.encode_attr('message')
    def chat(self, featurename, targetmode, target, message, **kwargs):
        ''' Send a text message to specific target, depending on targetmode '''
        self.socket.write('sendtextmessage targetmode={} target={} msg={}\n'.format(targetmode, target, message))
        self.socket.read_until('msg=ok', 2)

    @Escaper.encode_attr('message')
    def notify(self, featurename, message, **kwargs):
        ''' Send a message to this client '''
        self.socket.write('sendtextmessage targetmode=1 target={} msg={}\n'.format(self.clid, message))
        self.socket.read_until('msg=ok', 2)


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
