from ts3observer.models import Plugin, Action

import MySQLdb


class Meta:
    author_name = 'Tim Fechner'
    author_email = 'tim.b.f@gmx.de'
    version = '1.0'

class Config:
    enable = False
    interval = 5
    yaml = {
        'general': {
            'servergroup_id': 0,
            'remove_if_deleted': True,
        },
        'database': {
            'hostname': 'localhost',
            'username': '',
            'password': '',
            'database': '',
            'table': '',
        },
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
        auth_list = self.get_authenticated_users()

        for clid, client in clients.items():
            if (client.unique_identifier, True) in auth_list:
                if not self.already_has_group(client):
                    self.add_group(client)
            else:
                if self.already_has_group(client):
                    self.remove_group(client)

    def get_authenticated_users(self):
        self.cursor.execute('''SELECT ts3o_uid, ts3o_active FROM {}'''.format(self.config['database']['table']))
        self.connection.commit()
        users = self.cursor.fetchall()
        return [(pair['ts3o_uid'], bool(pair['ts3o_active'])) for pair in users]

    def already_has_group(self, client):
        for group in client.servergroups:
            if group == self.config['general']['servergroup_id']:
                return True
        return False

    def add_group(self, client):
        self._register_action(client, 'add')

    def remove_group(self, client):
        self._register_action(client, 'remove')

    def shutdown(self):
        self.connection.close()

    def _register_action(self, client, atype):
        Action(
            'Authenticater',
            ts3o.run_id,
            client,
            '{}_group'.format(atype),
            function_kwargs = {
                'servergroup_id': self.config['general']['servergroup_id'],
            },
            reason=atype
        ).register()
