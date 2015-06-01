''' Define some utils for all needs '''

import os
import time
import yaml
import logging
from ts3observer import Configuration
from ts3observer.exc import NoConfigFileException, QueryFailedException, NoMetaDataException, NoMetaAuthorNameException, \
                            NoMetaAuthorEmailException, NoMetaVersionException, NoDefaultConfigException, \
                            DefaultConfigisNotDictException


def path(string):
    ''' Return a relative path to any file in this project, given by string '''
    return '{}{}'.format(ts3o.base_path, string)

def get_available_plugins():
    available_plugins = []
    for f in os.listdir(ts3o.base_path + '/plugins'):
        if f.endswith('.py') and f != '__init__.py':
            available_plugins.append(os.path.splitext(f)[0])
    return available_plugins

def plugin_is_new(plugin_name):
    return not os.path.isfile('{}/conf/{}.yml'.format(ts3o.base_path, plugin_name))

def create_plugin_config(plugin_name, plugin_object):
    config_string = yaml.dump(plugin_object.default_config, default_flow_style=False)
    with open('{}/conf/{}.yml'.format(ts3o.base_path, plugin_name), 'w') as cfg:
        cfg.write(config_string)

def get_plugin_config(plugin_name):
    with open('{}/conf/{}.yml'.format(ts3o.base_path, plugin_name), 'r') as cfg:
        config = yaml.load(cfg.read())
    return config

def check_plugin_data(plugin_name, plugin_module, plugin_object):
    if not hasattr(plugin_module, 'Meta'):
        raise NoMetaDataException(plugin_name)
    if not hasattr(plugin_module.Meta, 'author_name'):
        raise NoMetaAuthorNameException(plugin_name)
    if not hasattr(plugin_module.Meta, 'author_email'):
        raise NoMetaAuthorEmailException(plugin_name)
    if not hasattr(plugin_module.Meta, 'version'):
        raise NoMetaVersionException(plugin_name)
    if not hasattr(plugin_object, 'default_config'):
        raise NoDefaultConfigException(plugin_name)
    if not type(plugin_object.default_config) == dict:
        raise DefaultConfigisNotDictException(plugin_name)


def get_and_set_global_config():
    ''' Get the global configuration and store it in the ts3o object.
        Do not call before a logging config is set because of the beauty.
    '''
    try:
        ts3o.config = Configuration(path('/conf/ts3observer.yml'))
    except IOError:
        raise NoConfigFileException()

def get_loglevel():
    if ts3o.args.verbose:
        return logging.DEBUG
    if ts3o.args.quiet:
        return logging.CRITICAL
    return logging.INFO

def control_cycles(start_timestamp, end_timestamp):
    cycle_interval = 1
    needed_time = end_timestamp - start_timestamp

    if needed_time < 1:
        time.sleep(1 - needed_time)


class TelnetUtils(object):
    ''' Provide som eutils for the telnet connection '''

    @staticmethod
    def string_to_dict(arg_str):
        ''' Map a string to a property dict '''
        pairs = arg_str.replace('error id', 'error_id', 1).split(' ')

        properties = {}
        for pair in pairs:
            if '=' in pair:
                segments = pair.split('=', 1)
                properties.update({segments[0]: segments[1]})
            else:
                properties.update({pair: None})
        return properties

    @staticmethod
    def check_dev_modus(fn):
        ''' use as decorator '''
        def log_only(self, *args, **kwargs):
            pass
        def wrapper(self, *args, **kwargs):
            if ts3o.args.dev:
                return log_only(self, *args, **kwargs)
            else:
                return fn(self, *args, **kwargs)
        return wrapper

    @staticmethod
    def validate_query(result):
        if not 'msg=ok' in result:
            response = TelnetUtils.string_to_dict(result)
            error_id = response['error_id']
            error_msg = Escaper.decode(response['msg'])
            raise QueryFailedException(msg='ErrorID: {}, ErrorMsg: \'{}\''.format(error_id, error_msg))
        return result

    @staticmethod
    def remove_linebreaks(string):
        ''' Remove unnecessary linebreaks (\r or \n) '''
        return string.replace('\n', ' ').replace('\r', ' ')


class Escaper(object):
    ''' Take care of teamspeak's special char escaping ...
        Official documentation found here:
        http://media.teamspeak.com/ts3_literature/TeamSpeak%203%20Server%20Query%20Manual.pdf
    '''

    escapetable = {
        r'\\': '\\',
        r'\/': r'/',
        r'\s': r' ',
        r'\p': r'|'
    }

    @classmethod
    def encode(cls, string):
        ''' Escape a normal string '''
        for escaped_char, normal_char in cls.escapetable.items():
            string = string.replace(normal_char, escaped_char)
        return string

    @staticmethod
    def encode_attr(*args):
        ''' Escape a row of named attributes.
            Designed to be used as decorator
        '''
        def attr_encoder(fn):
            def wrapper(*func_args, **func_kwargs):
                for arg in args:
                    func_kwargs[arg] = Escaper.encode(func_kwargs[arg])
                return fn(*func_args, **func_kwargs)
            return wrapper
        return attr_encoder

    @classmethod
    def decode(cls, string):
        ''' Format a escaped string to normal one '''
        for escaped_char in cls.escapetable:
            string = string.replace(escaped_char, cls.escapetable[escaped_char])
        return string

    @staticmethod
    def decode_attr(*args):
        ''' Format a row of named attributes of escaped string to normal ones.
            Designed to be used as decorator
        '''
        def attr_decoder(fn):
            def wrapper(*func_args, **func_kwargs):
                for arg in args:
                    func_kwargs[arg] = Escaper.decode(func_kwargs[arg])
                return fn(*func_args, **func_kwargs)
            return wrapper
        return attr_decoder
