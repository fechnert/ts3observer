'''
Created on Nov 9, 2014

@author: fechnert
'''

import yaml


class Configuration(dict):
    ''' Read and provide the yaml config '''

    def __init__(self, path):
        ''' Initialize the file '''
        with open(path, 'r') as f:
            self.update(yaml.load(f))
