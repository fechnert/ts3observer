''' This module builds objects out of nonsense '''

import re

from ts3observer.models import Client, Channel
from ts3observer.utils import Escaper


class ClientFactory(object):

    transformers = {
        'servergroups': lambda value: [int(res) for res in value.split(',')],
        'unique_identifier': Escaper.decode,
        'nickname': Escaper.decode,
    }

    @staticmethod
    def build(client_dict, clid, tn):
        c = Client(clid, tn)
        for key, value in client_dict.items():
            if not key: continue
            key = re.sub(r'^client_', '', key)

            if key in ClientFactory.transformers:
                value = ClientFactory.transformers[key](value)
            setattr(c, key, value)
        return c


class ChannelFactory(object):

    transformers = {}

    @staticmethod
    def build(channel_dict, cid, tn):
        c = Channel(cid, tn)
        for key, value in channel_dict.items():
            if not key: continue
            key = re.sub(r'^client_', '', key)

            if key in ChannelFactory.transformers:
                value = ChannelFactory.transformers[key](value)
            setattr(c, key, value)
        return c
