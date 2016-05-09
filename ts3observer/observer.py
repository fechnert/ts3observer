''' The main logic '''

import os
import yaml
import logging
import importlib

from ts3observer import telnet
from ts3observer.models import AbstractPlugin
from ts3observer.utils import get_available_plugins, plugin_is_new, create_plugin_config, get_plugin_config, check_plugin_data
from ts3observer.exc import PluginIsBroken


class Supervisor(object):

    def __init__(self):
        ''' prepare everything'''
        ts3o.run_id = 0
        self._setup()

        self._load_plugins()
        self._stop_if_new_plugin_detected()

        self._tn = telnet.TelnetInterface()
        self._connect()

    def _setup(self):
        self._force_client_update = True
        self._force_channel_update = True
        self._force_server_info_update = True
        ts3o._action_queue = list()

    def _connect(self):
        logging.info('Establish telnet connection')
        logging.info('  Connecting to \'{}:{}\''.format(ts3o.config['host'], ts3o.config['port']))
        self._tn.connect(ts3o.config['host'], ts3o.config['port'])
        logging.info('  Logging in as \'{}\''.format(ts3o.config['user']))
        self._tn.login(ts3o.config['user'], ts3o.config['pass'])
        logging.info('  Choosing virtual ts3 server \'{}\''.format(ts3o.config['serv']))
        self._tn.use_server_instance(ts3o.config['serv'])
        logging.info('  Changing displayname to \'{}\''.format(ts3o.config['displayname']))
        self._tn.change_display_name(ts3o.config['displayname'])
        logging.info('Successful logged in!')
        logging.info('---')

    def run(self):
        ''' Runs the ts3observer '''
        ts3o.run_id += 1
        self._update()
        self._run_plugins()
        self._check_action_queue()

    def _load_plugins(self):
        logging.info('Loading plugins')
        ts3o.loaded_plugins = {}
        ts3o.plugin_data = {}
        for plugin_name in get_available_plugins():
            m = importlib.import_module('plugins.' + plugin_name)
            p = getattr(m, plugin_name)
            check_plugin_data(plugin_name, m, p)

            if plugin_is_new(plugin_name):
                logging.info('  {} (v{}) [NEW]'.format(plugin_name, m.Meta.version))
                create_plugin_config(plugin_name, m)
                self._new_plugin = True
                continue
            else:
                logging.info('  {} (v{})'.format(plugin_name, m.Meta.version))

            c = get_plugin_config(plugin_name)
            ts3o.loaded_plugins[plugin_name] = p(c)
            ts3o.plugin_data[plugin_name] = {}
            ts3o.loaded_plugins[plugin_name]._setup()

    def _stop_if_new_plugin_detected(self):
        if hasattr(self, '_new_plugin'):
            if self._new_plugin: raise NewPluginDetected()

    def _run_plugins(self):
        for plugin_name, plugin_instance in ts3o.loaded_plugins.items():
            if ts3o.config['plugins'][plugin_name]['enable']:
                if ts3o.run_id % ts3o.config['plugins'][plugin_name]['interval'] == 0:
                    plugin_instance.run(self._clients, self._channels, self._server_info)

    def _check_action_queue(self):
        # Create in the following line a copy of the list because it's a bad idea to remove
        # items from a live list while iterating over it ...
        for action in list(ts3o._action_queue):
            if action.updated:
                if action.execute_run_id == ts3o.run_id:
                    action.execute()
                    self._force_update(action.object_instance_name)
                    ts3o._action_queue.remove(action)
                else:
                    action.updated = False
            else:
                logging.debug('{} removed'.format(action))
                ts3o._action_queue.remove(action)

    def _force_update(self, type_string):
        ''' Force an update of specific information '''
        setattr(self, '_force_{}_update'.format(type_string.lower()), True)

    def _update(self):
        if ts3o.run_id == 1:
            logging.info('Fetching complete server information ...')
        if self._client_update_necessary():
            self._update_clients()
        if self._channel_update_necessary():
            self._update_channels()
        if self._server_info_update_necessary():
            self._update_server_info()
        if ts3o.run_id == 1:
            logging.info('Finished.')
            logging.info('---')

    def _update_clients(self):
        logging.debug('Updating clients ...')
        self._clients = self._tn.get_connected_clients()
        ts3o._clients = self._clients
        self._force_client_update = False
        self._last_client_update = ts3o.run_id

    def _update_channels(self):
        logging.debug('Updating channels ...')
        self._channels = self._tn.get_existing_channels()
        ts3o._channels = self._channels
        self._force_channel_update = False
        self._last_channel_update = ts3o.run_id

    def _update_server_info(self):
        logging.debug('Updating server info ...')
        self._server_info = self._tn.get_serverinfo()
        ts3o._server_info = self._server_info
        self._force_server_info_update = False
        self._last_server_info_update = ts3o.run_id

    def _client_update_necessary(self):
        if self._force_client_update: return True
        if self._last_client_update + ts3o.config['update_interval']['client_list'] <= ts3o.run_id: return True
        return False

    def _channel_update_necessary(self):
        if self._force_channel_update: return True
        if self._last_channel_update + ts3o.config['update_interval']['channel_list'] <= ts3o.run_id: return True
        return False

    def _server_info_update_necessary(self):
        if self._force_server_info_update: return True
        if self._last_server_info_update + ts3o.config['update_interval']['server_info'] <= ts3o.run_id: return True
        return False

    def shutdown(self):
        logging.debug('Shut down Plugins:')
        for plugin_name, plugin_instance in ts3o.loaded_plugins.items():
            logging.debug('  '+plugin_name)
            plugin_instance.shutdown()
        self._tn.disconnect()


class PluginDisposer(object):
    ''' dispose plugin management '''

    def list(self):
        plugins = self.get_available_plugins()
        for plugin in plugins['available']:
            print '{:<20} ({:<5})'.format(plugin.name, plugin.version)

    def enable(self):
        pass

    def disable(self):
        pass

    def get_enabled_plugins(self):
        pass

    def get_available_plugins(self):
        plugins = {
            'available': [],
            'broken': [],
        }

        for d in os.listdir(ts3o.base_path + '/plugins')[::-1]:
            try:
                plugin = self._build_abstract_plugin(d)
                plugins['available'].append(plugin)
            except PluginIsBroken as e:
                plugins['broken'].append(d)

        return plugins

    def _build_abstract_plugin(self, plugin_directory):
        self._plugin_is_valid(plugin_directory)

        return AbstractPlugin(
            plugin_directory,
            self._get_plugin_metadata(plugin_directory)
        )

    def _plugin_is_valid(self, plugin_directory):
        if not all([
            os.path.isfile(ts3o.base_path + '/plugins/' + plugin_directory + '/__init__.py'),
            os.path.isfile(ts3o.base_path + '/plugins/' + plugin_directory + '/config.yml'),
            os.path.isfile(ts3o.base_path + '/plugins/' + plugin_directory + '/meta.yml'),
            os.path.isfile(ts3o.base_path + '/plugins/' + plugin_directory + '/' + plugin_directory + '.py'),
        ]):
            raise PluginIsBroken(plugin_directory)

    def _get_plugin_metadata(self, plugin_name):
        with open(ts3o.base_path + '/plugins/' + plugin_name + '/meta.yml') as f:
            metadata = yaml.load(f)
        return metadata
