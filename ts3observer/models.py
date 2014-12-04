'''
Created on Dec 1, 2014

@author: fechnert
'''

import logging
from helpers import Escaper


class Client(object):
    ''' Represents the client '''

    def __init__(self, clid, socket, **kwargs):
        ''' Fill the object dynamically with client attributes got from telnet '''
        self.clid = clid
        self.socket = socket
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return '<Client object ({}: {})>'.format(self.clid, self.client_nickname)

    @Escaper.encode_attr('reason')
    def kick(self, featurename, reasonid, reason='ByeBye', **kwargs):
        ''' Kick a client '''
        self.socket.write('clientkick reasonid={} reasonmsg={} clid={}\n'.format(reasonid, reason, self.clid))
        self.socket.read_until('msg=ok', 2)
        logging.info('Feature \'{}\' kicked {}'.format(featurename, self.client_nickname))

    def move(self, featurename, to, **kwargs):
        ''' Move a client :to: a channel '''
        if int(self.cid) != to:
            ocid = self.cid
            self.socket.write('clientmove cid={} clid={}\n'.format(to, self.clid))
            self.socket.read_until('msg=ok', 2)
            logging.info('Feature \'{}\' moved {} (from cid {} to {})'.format(featurename, self.client_nickname, ocid, to))

    @Escaper.encode_attr('reason')
    def ban(self, featurename, time=0, reason='Kicked', **kwargs):
        ''' Ban a client for :sfor: seconds '''
        if time:
            self.socket.write('banclient clid={} banreason={} time={}\n'.format(self.clid, reason, time))
        else:
            self.socket.write('banclient clid={} banreason={}\n'.format(self.clid, reason))
        self.socket.read_until('msg=ok', 2)
        logging.info('Feature \'{}\' banned {} for {} seconds (0 = infinite)'.format(featurename, self.client_nickname, time))

    def show(self, featurename, **kwargs):
        ''' Only shows the clientname (for debugging purpose) '''
        logging.info('{}: {}'.format(featurename, Escaper.decode(self.client_nickname)))


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
