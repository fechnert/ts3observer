''' The main logic '''

import logging

from ts3observer import telnet


class Supervisor(object):

    def __init__(self):
        ''' prepare everything'''
        ts3o.run_id = 0
        self._setup()

        self._tn = telnet.TelnetInterface()
        self._connect()

    def _setup(self):
        self._clients = None
        self._channels = None
        self._server_info = None

    def _connect(self):
        logging.info('Establish telnet connection')
        self._tn.connect(ts3o.config['host'], ts3o.config['port'])
        self._tn.login(ts3o.config['user'], ts3o.config['pass'])
        self._tn.use_server_instance(ts3o.config['serv'])
        self._tn.change_display_name(ts3o.config['displayname'])
        logging.info('Successful logged in!')

    def run(self):
        ''' 1)   get actual clientlist
            2)   check if channellist is old:
            2.1)    get actual channellist
            3)   check if serverinfo is old:
            3.1)    get actual serverinfo
            4)   poke all plugins with data (threaded?)
        '''
        ts3o.run_id += 1
        self._update()

    def _update(self):
        if self._client_update_necessary():
            self._update_clients()
        if self._channel_update_necessary():
            self._update_channels()
        if self._server_info_update_necessary():
            self._update_server_info()

    def _update_clients(self):
        logging.debug('Updating clients ...')
        self._clients = self._tn.get_connected_clients()
        self._last_client_update = ts3o.run_id

    def _update_channels(self):
        logging.debug('Updating channels ...')
        self._channels = self._tn.get_existing_channels()
        self._last_channel_update = ts3o.run_id

    def _update_server_info(self):
        logging.debug('Updating server info ...')
        self._server_info = self._tn.get_serverinfo()
        self._last_server_info_update = ts3o.run_id

    def _client_update_necessary(self):
        if self._clients == None: return True
        if self._last_client_update + ts3o.config['update_interval']['client_list'] <= ts3o.run_id: return True
        return False

    def _channel_update_necessary(self):
        if self._channels == None: return True
        if self._last_channel_update + ts3o.config['update_interval']['channel_list'] <= ts3o.run_id: return True
        return False

    def _server_info_update_necessary(self):
        if self._server_info == None: return True
        if self._last_server_info_update + ts3o.config['update_interval']['server_info'] <= ts3o.run_id: return True
        return False

    def shutdown(self):
        self._tn.disconnect()
