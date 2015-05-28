''' The Config part '''

import yaml


class Configuration(dict):
    ''' Read and provide a yaml config '''

    def __init__(self, path):
        ''' Initialize the file '''
        with open(path, 'r') as f:
            self.update(yaml.load(f))
