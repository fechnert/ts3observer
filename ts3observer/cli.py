''' The cli module that will interact with your bash. '''

import re
import sys
import time
import logging
from prettytable import PrettyTable, NONE

from ts3observer.observer import Supervisor, PluginDisposer
from ts3observer.telnet import TelnetInterface
from ts3observer.utils import TelnetUtils, Escaper, path, get_and_set_global_config, get_loglevel, control_cycles
from ts3observer.exc import ShutDownException


class CommandLineInterface(object):
    ''' The cli will interact with your bash '''

    def __init__(self):
        self._set_logging_config()
        get_and_set_global_config()

    def _set_logging_config(self):
        ''' Set the basic logging config '''
        logging.basicConfig(
            stream=sys.stdout,
            level=get_loglevel(),
            format=' %(asctime)s | %(levelname)8s | %(message)s',
            datefmt='%d.%m.%Y - %H:%M:%S'
        )

    def run(self):
        ''' Run the ts3observer bot '''
        logging.info('Starting ts3observer')
        supervisor = Supervisor()
        while True:
            try:
                self._cycle(supervisor)
            except KeyboardInterrupt as e:
                print ''
                logging.info('Shutting down')
                supervisor.shutdown()
                raise ShutDownException()

    def _cycle(self, supervisor):
        start_timestamp = time.time()
        supervisor.run()
        end_timestamp = time.time()
        control_cycles(start_timestamp, end_timestamp)

    def utils(self):
        print getattr(CliHelper(), ts3o.args.utils)()

    def plugins(self):
        getattr(PluginDisposer(), ts3o.args.plugins)()

    def version(self):
        f = open(path('/.version'), 'r')
        print(f.read().rstrip('\r\n'))
        f.close()


class CliHelper(object):

    def __init__(self):
        print('Connecting ...')
        self.tn = TelnetInterface()
        self.tn.connect(ts3o.config['host'], ts3o.config['port'])
        self.tn.login(ts3o.config['user'], ts3o.config['pass'])
        self.tn.use_server_instance(ts3o.config['serv'])

    def servergrouplist(self):
        groups = self.tn._query('servergrouplist').split('|')
        table = PrettyTable(['sgid', 'name', 'type', 'sortid'], vrules=NONE)
        table.align = 'l'
        types = ['Template', 'Real Group', 'Query Group']
        for group in groups:
            g = TelnetUtils.string_to_dict(group)
            table.add_row([g['sgid'], Escaper.decode(g['name']), types[int(g['type'])], g['sortid']])
        return table

    def channellist(self):
        channels = self.tn._query('channellist').split('|')
        table = PrettyTable(['cid', 'pid', 'name', 'clients'], vrules=NONE)
        table.align = 'l'
        for channel in channels:
            c = TelnetUtils.string_to_dict(channel)
            table.add_row([c['cid'], c['pid'], self.get_channelname(c['channel_name']), c['total_clients']])
        return table

    def get_channelname(self, name):
        name = Escaper.decode(name)
        return re.sub(r'\[(cspacer|\*spacer)[0-9]*\]', '', name)

    def clientlist(self):
        clients = self.tn._query('clientlist').split('|')
        if ts3o.args.advanced:
            return self._clientlist_advanced(clients)
        else:
            return self._clientlist(clients)

    def _clientlist_advanced(self, clients):
        table = PrettyTable(['name', 'attribute', 'value'], vrules=NONE)
        table.align = 'l'
        for client in clients:
            c = TelnetUtils.string_to_dict(client)
            clid = c['clid']
            if int(c['client_database_id']) == 1: continue
            c = TelnetUtils.string_to_dict(self.tn._query('clientinfo clid={}'.format(c['clid'])))
            table.add_row([Escaper.decode(c['client_nickname']), 'clid', clid])
            c.pop('client_nickname', None)
            for key, value in c.items():
                if not key: continue
                table.add_row(['', key, value])
            table.add_row(['', '', ''])
        return table

    def _clientlist(self, clients):
        table = PrettyTable(['clid', 'cldbid', 'name', 'channel', 'type'], vrules=NONE)
        table.align = 'l'
        for client in clients:
            c = TelnetUtils.string_to_dict(client)
            table.add_row([c['clid'], c['client_database_id'], Escaper.decode(c['client_nickname']), c['cid'], c['client_type']])
        return table
