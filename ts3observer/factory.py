''' This module builds objects out of nonsense '''

import re

from ts3observer.models import Client, Channel


class ClientFactory(object):

    @staticmethod
    def build(client_dict, clid, tn):
        c = Client(clid, tn)
        for key, value in client_dict.items():
            if key:
                setattr(c, re.sub('^client_', '', key), value)
        return c



class ChannelFactory(object):

    @staticmethod
    def build(channel_dict, cid, tn):
        c = Channel(cid, tn)
        for key, value in channel_dict.items():
            if key:
                setattr(c, re.sub('^channel_', '', key), value)
        return c
