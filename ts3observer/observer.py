'''
Created on Nov 9, 2014

@author: fechnert
'''

import os, shutil
import yaml
import logging
import telnetlib
import features
import time
import telnet
from utils import Escaper, PropertyMapper
from models import Client, Channel


class Configuration(dict):
    ''' Read and provide the yaml config '''

    def __init__(self, path):
        ''' Initialize the file '''
        self._check_local_conf()
        with open(path, 'r') as f:
            self.update(yaml.load(f))

    def _check_local_conf(self):
        ''' Check if a local config file is existing '''
        if not os.path.exists('config.yml'):
            self._create_local_conf()

    def _create_local_conf(self):
        ''' Create a local config out of the example '''
        shutil.copy2('example.config.yml', 'config.yml')
        logging.warn('local \'config.yml\' not found! But i\'ve created one for you ;)')
        logging.warn('But before we start, please configure the configuration file. Stopping here ...')
        exit(1)


class Supervisor(object):
    ''' Guide the different features to do their work '''

    def __init__(self):
        ''' Initialize the Config '''
        self.config = Configuration('config.yml')
        self.queue = {}
        self.work_interval = self.config['global']['work_interval']
        self.telnet = telnet.TelnetInterface()
        self._connect()

    def _connect(self):
        ''' Connect to server '''
        conf = self.config['global']['telnet']
        self.telnet.connect(conf['host'], conf['port'])
        self.telnet.login(conf['user'], conf['pass'])
        self.telnet.choose_vserv(conf['serv'])
        self.telnet.change_displayname(conf['display_name'])
        logging.info('Successfully connected!')

    def execute(self):
        self.clients = self._clientlist()
        channels = None

        self._call_features(self.clients, channels)
        self._workoff_queue()

        return self.clients

    def _clientlist(self):
        ''' Build a list of clients '''
        clients = {}
        for client_info in self.telnet.get_clientlist():
            clid = client_info['clid']
            clients.update({clid: self.telnet.get_client(clid)})
        return clients

    def _call_features(self, clients, channels):
        ''' Call every signed feature '''
        for feature in self.__import_features(clients, channels).values():
            try:
                feature.run()
            except NotImplementedError:
                logging.warn('Can\'t run Feature \'{}\''.format(feature.__class__.__name__))

    def __import_features(self, clients, channels):
        ''' Import only the needed features '''
        feature_objects = {}
        for feature in self.__get_enabled_features():
            feature_objects.update({
                feature: getattr(features, feature)(
                    self.config['features'][feature],
                    self.config['features']['Base']['rules'],
                    self.queue,
                    clients,
                    channels
                    )
            })
        return feature_objects

    def __get_enabled_features(self):
        ''' Get all features which are enabled in config '''
        features = []
        for feature in self.config['features']:
            if feature != 'Base':
                if self.config['features'][feature]['enable']:
                    features.append(feature)
        return features

    def _workoff_queue(self):
        ''' Work off the queue and execute outstanding actions '''
        for actionname, action in self.queue.items():
            if action.last_triggered <= (time.time() - self.config['global']['work_interval']):
                if actionname in self.queue:
                    self.queue.pop(actionname)
            if action.trigger_time <= time.time():
                self.__execute_action(action)
                if actionname in self.queue:
                    self.queue.pop(actionname)

    def __execute_action(self, action):
        ''' Call the action of an clientaction '''
        getattr(self.telnet, 'clientaction_{}'.format(action.additional_params['action']))(
            action.client_obj,
            action.featurename,
            **action.additional_params
        )
