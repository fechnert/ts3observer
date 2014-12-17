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
        logging.warn('local \'config.yml\' not found! But i\'ve created one for you ;)')
        shutil.copy2('example.config.yml', 'config.yml')


class Supervisor(object):
    ''' Guide the different features to do their work '''

    def __init__(self):
        ''' Initialize the Config '''
        self.config = Configuration('config.yml')
        self.queue = {}
        self.work_interval = self.config['global']['work_interval']
        self._connect()

    def _connect(self):
        ''' Connect to the telnet server from ts3 '''
        conf = self.config['global']['telnet']
        self.tn = telnetlib.Telnet(conf['host'], conf['port'])
        self.query('login {} {}'.format(conf['user'], conf['pass']))
        self.query('use {}'.format(conf['serv']))

    def execute(self):
        self.clients = self._clientlist()
        channels = None
        self._call_features(self.clients, channels)
        logging.debug('Clients: {}'.format(str(self.clients)))
        logging.debug('Queue  : {}'.format(str(self.queue)))
        self.workoff_queue()

    def workoff_queue(self):
        ''' Work off the queue and execute outstanding actions '''
        for actionname, action in self.queue.items():
            if action.last_triggered <= (time.time() - self.config['global']['work_interval']):
                if actionname in self.queue:
                    self.queue.pop(actionname)
            if action.trigger_time <= time.time():
                action.execute()
                if actionname in self.queue:
                    self.queue.pop(actionname)

    def _call_features(self, clients, channels):
        ''' Call every signed feature '''
        for feature in self._import_features(clients, channels).values():
            try:
                feature.run()
            except NotImplementedError:
                logging.warn('Can\'t run Feature \'{}\''.format(feature.__class__.__name__))

    def _import_features(self, clients, channels):
        ''' Import only the needed features '''
        feature_objects = {}
        for feature in self._get_enabled_features():
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

    def _get_enabled_features(self):
        ''' Get all features which are enabled in config '''
        features = []
        for feature in self.config['features']:
            if feature != 'Base':
                if self.config['features'][feature]['enable']:
                    features.append(feature)
        return features

    def _clientlist(self):
        ''' collect all connected clients '''
        raw_clients = self.query('clientlist').split('|')
        clients = {}
        for raw_client in raw_clients:
            clients.update(self.__build_client(raw_client))
        return clients

    def __build_client(self, raw_client):
        ''' build a client from "clientlist" command '''
        clid = int(PropertyMapper.string_to_dict(raw_client)['clid'])
        raw_client_data = self.query('clientinfo clid={}'.format(clid))
        client_data = PropertyMapper.string_to_dict(raw_client_data)
        client = Client(clid, self.tn, **client_data)
        return {clid: client}

    def query(self, command):
        ''' Executes the telnet server queries '''
        self.tn.write('{}\n'.format(command))
        result = self.tn.read_until('msg=ok', 2)
        return Escaper.remove_linebreaks(result)
