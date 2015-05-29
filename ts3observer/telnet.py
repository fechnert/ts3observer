''' Here we will speak in telnet ... '''

import logging
import time
import telnetlib

from ts3observer.factory import ClientFactory, ChannelFactory
from ts3observer.utils import TelnetUtils, Escaper
from ts3observer.exc import QueryFailedException


class TelnetInterface(object):
    ''' Provide a interface for the telnet connection '''

    def __init__(self):
        self.tn = None

    #####
    # Connection stuff

    def connect(self, host, port):
        ''' Connect with the teamspeak server instance '''
        logging.info('  Connecting to \'{}:{}\''.format(host, port))
        self.tn = telnetlib.Telnet(host, port)
        time.sleep(1)  # Ugly, know ... but telnet is slow
        self.tn.read_very_eager()  # clear cache

    def login(self, user, password):
        ''' Log into the teamspeak server instance as given user with password '''
        logging.info('  Logging in as \'{}\''.format(user))
        self._query('login {} {}'.format(user, password))

    def use_server_instance(self, servid):
        ''' Use a ts3 server instance '''
        logging.info('  Choosing virtual ts3 server \'{}\''.format(servid))
        self._query('use {}'.format(servid))

    def change_display_name(self, name):
        ''' Change the nickname of the bot '''
        logging.info('  Changing displayname to \'{}\''.format(name))
        uname = Escaper.encode(name)
        self._query('clientupdate client_nickname={}'.format(uname))

    def disconnect(self):
        ''' Quits the connection the soft way '''
        logging.info('Closing the connection')
        self._query('quit')


    #####
    # Stuff to obtain information

    def get_clientlist(self):
        ''' Get the list of all current connected clients '''
        raw_clientlist = self._query('clientlist').split('|')

        clientlist = []
        for raw_client in raw_clientlist:
            properties = TelnetUtils.string_to_dict(raw_client)
            clientlist.append(int(properties['clid']))
        return clientlist

    def get_clientinfo(self, clid):
        raw_client = self._query('clientinfo clid={}'.format(clid))
        return TelnetUtils.string_to_dict(raw_client)

    def get_connected_clients(self):
        ''' Returns all connected clients as objects '''
        connected_clients = {}
        for clid in self.get_clientlist():
            client_dict = self.get_clientinfo(clid)
            connected_clients.update({clid: ClientFactory.build(client_dict, clid, self)})
        return connected_clients

    def get_channellist(self):
        raw_channellist = self._query('channellist').split('|')

        channellist = []
        for raw_channel in raw_channellist:
            properties = TelnetUtils.string_to_dict(raw_channel)
            channellist.append(int(properties['cid']))
        return channellist

    def get_channelinfo(self, cid):
        raw_channel = self._query('channelinfo cid={}'.format(cid))
        return TelnetUtils.string_to_dict(raw_channel)

    def get_existing_channels(self):
        ''' Returns all connected channels as objects '''
        existing_channels = {}
        for cid in self.get_channellist():
            channel_dict = self.get_channelinfo(cid)
            existing_channels.update({cid: ChannelFactory.build(channel_dict, cid, self)})
        return existing_channels

    def get_serverinfo(self):
        raw_server_info = self._query('serverinfo')
        return TelnetUtils.string_to_dict(raw_server_info)

    @TelnetUtils.check_dev_modus
    def _query(self, command):
        ''' For internal usage to simplify telnet queries '''
        #logging.debug('TelnetQuery: {}'.format(command))
        self.tn.write('{}\n'.format(command))
        try:
            query_result = self.tn.read_until('msg=ok', 2)
            raw_result = TelnetUtils.remove_linebreaks(query_result)
            result = TelnetUtils.validate_query(raw_result)

        except QueryFailedException as e:
            raise QueryFailedException(command, e.msg)

        return result
