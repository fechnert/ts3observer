from ts3observer.models import Plugin, Action

import MySQLdb
import logging
from datetime import datetime


class Meta:
    author_name = 'Tim Fechner'
    author_email = 'tim.b.f@gmx.de'
    version = '1.3.1'

class Config:
    enable = False
    interval = 30
    yaml = {
        'database': {
            'hostname': 'localhost',
            'username': '',
            'password': '',
            'database': '',
            'table': '',
        },
        'general': {
            'remove_groups_if_not_in_database': True,
            'default_group': 8
        },
        'extra': {
            'save_client_data': False,
            'nickname_fieldname': 'ts3o_nickname',
            'last_seen_fieldname': 'ts3o_last_seen',
            'timestamp_format': '%Y-%m-%d %H:%M:%S'
        },
        'groups': {
            'member': 19,
            'vip': 32,
        }
    }

class Authenticater(Plugin):

    def setup(self):
        self.connection = MySQLdb.connect(
            host=self.config['database']['hostname'],
            user=self.config['database']['username'],
            passwd=self.config['database']['password'],
            db=self.config['database']['database']
        )
        self.cursor = self.connection.cursor(MySQLdb.cursors.DictCursor)

    def run(self, clients, channels, server_info):
        users = self.get_users()

        for clid, client in clients.items():
            if not client.unique_identifier in users:
                self.remove_all_groups(client)
                continue

            if self.config['extra']['save_client_data']:
                self.write_client_data(client)

            for group_name, group in self.config['groups'].items():
                if not group in client.servergroups and users[client.unique_identifier][group_name]:
                    self.add_group(client, group)
                elif group in client.servergroups and not users[client.unique_identifier][group_name]:
                    self.remove_group(client, group)

    def get_users(self):
        groups = [group for group, sgid in self.config['groups'].items()]
        tables = ', '.join(['ts3o_'+name for name in groups])
        self.cursor.execute('''SELECT ts3o_uid, {} FROM {}'''.format(tables, self.config['database']['table']))
        self.connection.commit()
        users = self.cursor.fetchall()
        return {user['ts3o_uid']:{name:bool(user['ts3o_'+name]) for name in groups} for user in users}

    def add_group(self, client, sgid):
        self._register_action(client, 'add', sgid)

    def remove_group(self, client, sgid):
        self._register_action(client, 'remove', sgid)

    def remove_all_groups(self, client):
        if not self.config['general']['remove_groups_if_not_in_database']:
            return

        for sgid in client.servergroups:
            if sgid == self.config['general']['default_group']:
                continue
            self.remove_group(client, sgid)

    def write_client_data(self, client):
        self.cursor.execute('''UPDATE {table} SET {nickname_fieldname} = '{client.nickname}' WHERE ts3o_uid = '{client.unique_identifier}' '''.format(
            table = self.config['database']['table'],
            nickname_fieldname = self.config['extra']['nickname_fieldname'],
            client = client
        ))
        self.cursor.execute('''UPDATE {table} SET {last_seen_fieldname} = '{timestamp}' WHERE ts3o_uid = '{uid}' '''.format(
            table = self.config['database']['table'],
            last_seen_fieldname = self.config['extra']['last_seen_fieldname'],
            timestamp = datetime.now().strftime(self.config['extra']['timestamp_format']),
            uid = client.unique_identifier
        ))
        self.connection.commit()

    def shutdown(self):
        self.connection.close()

    def _register_action(self, client, atype, sgid):
        Action(
            'Authenticater',
            ts3o.run_id,
            client,
            '{}_group'.format(atype),
            function_kwargs = {
                'servergroup_id': sgid,
            },
            reason='{}_{}'.format(atype, sgid)
        ).register()
