from ts3observer.models import Plugin, Action

import MySQLdb
import logging


class Meta:
    author_name = 'Tim Fechner'
    author_email = 'tim.b.f@gmx.de'
    version = '1.1'

class Config:
    enable = False
    interval = 5
    yaml = {
        'database': {
            'hostname': 'localhost',
            'username': '',
            'password': '',
            'database': '',
            'table': '',
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
            if not client.unique_identifier in users: continue

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
            reason=atype
        ).register()
