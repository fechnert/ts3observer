'''
Created on Dec 1, 2014

@author: fechnert
'''

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

    def kick(self, reasonid, reason='ByeBye'):
        ''' Kick a client '''
        self.socket.write('clientkick reasonid={} reasonmsg={} clid={}\n'.format(reasonid, reason, self.clid))
        self.socket.read_until('msg=ok', 2)

    def move(self, to):
        ''' Move a client :to: a channel '''
        self.socket.write('clientmove cid={} clid={}\n'.format(to, self.clid))
        self.socket.read_until('msg=ok', 2)

    def ban(self, time=0, reason='Kicked'):
        ''' Ban a client for :sfor: seconds '''
        if time:
            self.socket.write('banclient clid={} banreason={} time={}\n'.format(self.clid, reason, time))
        else:
            self.socket.write('banclient clid={} banreason={}\n'.format(self.clid, reason))
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
