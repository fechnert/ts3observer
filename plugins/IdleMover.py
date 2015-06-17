from ts3observer.models import Plugin, Action


class Meta:
    author_name = 'Tim Fechner'
    author_email = 'tim.b.f@gmx.de'
    version = '1.1'


class IdleMover(Plugin):

    default_config = {
        'general': {
            'afk_channel_id': 0,
            'lobby_channel_id': 0,
        },
        'listeners': {
            'check_away': {
                'enable': True,
                'move_after': 0
            },
            'check_idle': {
                'enable': True,
                'move_after': 900
            },
            'check_deaf': {
                'enable': True,
                'move_after': 0
            },
            'check_muted': {
                'enable': False,
                'move_after': 1800
            }
        }
    }

    def setup(self):
        self.brain.update({'move_origins':{}})

    def run(self, clients, channels, server_info):
        for clid, client in clients.items():
            if not any([
                self.check_status(client, 'check_away', 'is_away'),
                self.check_status(client, 'check_idle', 'is_idle'),
                self.check_status(client, 'check_deaf', 'is_deaf'),
                self.check_status(client, 'check_muted', 'is_muted'),
            ]):
                if self._in_afk_channel(client):
                    self.move_back(client)

    def check_status(self, client, name, attr):
        if self.config['listeners'][name]['enable']:
            if getattr(client, attr)():
                if not self._in_afk_channel(client):
                    self.move(client, name)
                    self.brain['move_origins'].update({int(client.id): int(client.cid)})
                return True

    def move(self, client, function_name):
        Action(
            'IdleMover',
            ts3o.run_id + self.config['listeners'][function_name]['move_after'],
            client,
            'move',
            function_kwargs = {
                'target_channel_id': self.config['general']['afk_channel_id'],
            },
            reason=function_name
        ).register()

    def move_back(self, client):
        if int(client.id) in self.brain['move_origins']:
            origin = self.brain['move_origins'][int(client.id)]
        else:
            origin = self.config['general']['lobby_channel_id']

        Action(
            'IdleMover',
            ts3o.run_id,
            client,
            'move',
            function_kwargs = {
                'target_channel_id': origin,
            },
            reason='move_back'
        ).register()

    def _in_afk_channel(self, client):
        return int(client.cid) == self.config['general']['afk_channel_id']
