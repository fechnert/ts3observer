'''
Created on Nov 9, 2014

@author: fechnert
'''

import yaml
import logging
import features


class Configuration(dict):
    ''' Read and provide the yaml config '''

    def __init__(self, path):
        ''' Initialize the file '''
        with open(path, 'r') as f:
            self.update(yaml.load(f))


class Supervisor(object):
    ''' Guide the different features to do their work '''

    def __init__(self):
        ''' Initialize the Config '''
        self.config = Configuration('config.yml')

    def execute(self):
        for feature in self._import_features().values():
            try:
                feature.run()
            except NotImplementedError:
                logging.warn('Can\'t run Feature \'{}\''.format(feature.__class__.__name__))

    def _get_enabled_features(self):
        ''' Get all features which are enabled in config '''
        features = []
        for feature in self.config['features']:
            if self.config['features'][feature]['enable']:
                features.append(feature)
        return features

    def _import_features(self):
        ''' Import only the needed features '''
        feature_objects = {}
        for feature in self._get_enabled_features():
            feature_objects.update({
                feature: getattr(features, feature)(self.config['features'][feature])
            })
        return feature_objects


class Client(object):
    ''' Represents the client '''

    def __init__(self, **kwargs):
        ''' Fill the object dynamically with client attributes got from telnet '''
        for key, value in kwargs.items():
            setattr(self, key, value)


class Channel(object):
    ''' Represents the Channel '''

    def __init__(self, **kwargs):
        ''' Fill the object dynamically with channel attributes got from telnet '''
        for key, value in kwargs.items():
            setattr(self, key, value)
